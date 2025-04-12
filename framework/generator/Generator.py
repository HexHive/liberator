import os, json

from driver.ir import ApiCall
from driver.factory import EmptyDriverSpace
class Generator:
    def __init__(self, config):
        config.build_data_layout()
        config.build_condition_manager()

        self._workdir       = config.work_dir
        self._metadata_dir  = config.metadata_dir
        self._factory       = config.factory
        self._backend       = config.backend
        self._pool          = config.pool

        self._config = config
        
    def run(self):
        # print("Cleaning previous drivers...")
        # shutil.rmtree(self._backend.working_dir + "/*")
        # shutil.rmtree(self._backend.seeds_dir + "/*")

        print("Generating drivers...")

        while not self._pool.full():
            try:
                self._pool.add_driver(self._factory.create_random_driver())
            except EmptyDriverSpace as ex:
                print(f"Impossible to produce more than {len(self._pool)} drivers!")
                break

        print(f"I have done {len(self._pool)} drivers!")

        api_freq = dict([(x, 0) for x in self._factory.dependency_graph.keys()])
        dist_apis = set()

        while not self._pool.empty():
            driver = self._pool.pop()

            driver_name = self._backend.get_name()

            print(f"Storing driver: {driver_name}") 
            self._backend.emit_driver(driver, driver_name)

            print(f"Storing seeds for: {driver_name}")
            self._backend.emit_seeds(driver, driver_name)

            for api, freq in driver.get_apis_multiset().items():
                api_freq[api] = freq
                dist_apis.add(api)

            print(f"Storing metadata for {driver_name}:")
            self.dump_metadata(driver, driver_name)

    def dump_metadata(self, driver, driver_name):

        if "." in driver_name:
            ext_pos = driver_name.find(".")
            driver_name_clean = driver_name[:ext_pos]
        else:
            driver_name_clean = driver_name

        driver_meta = f"{driver_name_clean}.meta"
        
        meta_file = os.path.join(self._metadata_dir, driver_meta)

        metadata = {}
        metadata["api_multiset"] = {}
        for api, freq in driver.get_apis_multiset().items():
            metadata["api_multiset"][api.function_name] = freq
        
        with open(meta_file, "w") as fp:
            json.dump(metadata, fp)
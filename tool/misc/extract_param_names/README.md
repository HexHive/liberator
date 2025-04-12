# Parameter Names Extractor


## Initialization
```python 
# include_folder: folder where all the header files are located. stub C++ file with just empty main will be created where all the headers are included.
# input_file: output from condition_extractor tool
extractor = ParamNamesExtractor(include_folder, input_file)
```

## Public Functions
* `get_field_names_for_all_functions(self, output_file='')`
    * returns field names for all function in input file
    * optinally writes output to output_file, if specified
* `get_field_names_for_a_function(self, function_name)`
    * returns field names for just a given function
* `get_field_name_using_class_type_and_index(self, class_name, index)`
    * returns field type and name using given class and index of a field inside this class.

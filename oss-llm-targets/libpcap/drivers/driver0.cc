#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <errno.h>

#include <pcap.h>
#include <pcap/pcap.h>
#include <pcap/bpf.h>

#ifdef __cplusplus
extern "C" {
#endif


FILE * outfile = NULL;
char * errbuf;

void fuzz_openFile(const char * name) {
    if (outfile != NULL) {
        fclose(outfile);
    }
    outfile = fopen(name, "w");
}

void sock_initfuzz(const uint8_t *Data, size_t Size);
int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size); /* required by C89 */
int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    pcap_if_t * pkts;
    int is_ours;
    char errbuf[PCAP_ERRBUF_SIZE];
    const u_char *pkt;
    struct pcap_pkthdr *header;
    struct pcap_stat stats;
    int r;

    //initialization
    if (outfile == NULL) {
        fuzz_openFile("/dev/null");
    }

    sock_initfuzz(Data, Size);
    //initialize structure
    //is_ours = pcap_findalldevs(&pkts, errbuf);
    if (is_ours < 0) {
        fprintf(outfile, "Couldn't open pcap file %s\n", errbuf);
        return 0;
    }

    //loop over packets
    //r = pcap_next_ex(pkts, &header, &pkt);
    //while (r > 0) {
    //    fprintf(outfile, "packet length=%d/%d\n",header->caplen, header->len);
    //    r = pcap_next_ex(pkts, &header, &pkt);
    //}
    //if (pcap_stats(pkts, &stats) == 0) {
    //    fprintf(outfile, "number of packets=%d\n", stats.ps_recv);
    //}
    ////close structure
    //pcap_close(pkts);
    //pcap_t *netfilter_create(const char *device, char *ebuf, int *is_ours);
    return 0;
}

void sock_initfuzz(const uint8_t *Data, size_t Size) {
    //do nothing
}

#ifdef __cplusplus
}
#endif

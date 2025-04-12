#include <pcap.h>
#include <pcap/pcap.h>

#include <string.h>

int main() {
    char  errbuf[PCAP_ERRBUF_SIZE] = { 0 };
    pcap_if_t *allDevs;
    
    return pcap_findalldevs_ex("file://missing_file", NULL, &allDevs, errbuf);
}

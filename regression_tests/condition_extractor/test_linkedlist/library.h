
#include <stdlib.h>
#include <inttypes.h>

// typedef struct linked_list {
//     struct linked_list *next;
//     char payload;
// } my_linked_list;

// typedef struct a_struct {
//     my_linked_list *list;
//     int field_a;
//     int field_b;
// } my_struct;

typedef struct client_info {
    struct client_info *next;
    void *data;
    char *name;
} TIFFClientInfoLink;

typedef struct tiff {
	char*                tif_name;         /* name of open file */
	int                  tif_fd;           /* open file descriptor */
	int                  tif_mode;         /* open mode (O_*) */
	uint32_t               tif_flags;
	uint64_t*              tif_dirlist;      /* list of offsets to already seen directories to prevent IFD looping */
	uint16_t               tif_dirlistsize;  /* number of entries in*/TIFFClientInfoLink*  tif_clientinfo;   /* extra client information. */
	/* Backward compatibility stuff. We need these two fields for
	 * setting up an old tag extension scheme. */
	size_t               tif_nfieldscompat;
} TIFF;
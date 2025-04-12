
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

typedef struct tiff TIFF;

typedef void (*TIFFUnmapFileProc)(void*, void* base, uint32_t size);

typedef void (*TIFFVoidMethod)(TIFF*);

typedef struct client_info {
    struct client_info *next;
    void *data;
    char *name;
} TIFFClientInfoLink;


typedef struct _TIFFField {
	uint32_t field_tag;                       /* field's tag */
	short field_readcount;                  /* read count/TIFF_VARIABLE/TIFF_SPP */
	short field_writecount;                 /* write count/TIFF_VARIABLE */
	unsigned short field_bit;   
	char* field_name;          
} TIFFField;

typedef struct _TIFFFieldArray {
	// TIFFFieldArrayType type;    /* array type, will be used to determine if IFD is image and such */
	uint32_t allocated_size;      /* 0 if array is constant, other if modified by future definition extension support */
	uint32_t count;               /* number of elements in fields array */
	TIFFField* fields;          /* actual field info */
} TIFFFieldArray;

struct tiff {
	char*                tif_name;         /* name of open file */
	int                  tif_fd;           /* open file descriptor */
	int                  tif_mode;         /* open mode (O_*) */
	uint32_t               tif_flags;
	uint64_t*              tif_dirlist;      /* list of offsets to already seen directories to prevent IFD looping */
	uint16_t               tif_dirlistsize;  /* number of entries in*/TIFFClientInfoLink*  tif_clientinfo;   /* extra client information. */
	uint8_t*               tif_rawdata;
	TIFFField**          tif_fields;       /* sorted table of registered tags */
	size_t               tif_nfields;      /* # entries in  tag table*/
	size_t               tif_nfieldscompat;
	TIFFVoidMethod       tif_cleanup;      /* cleanup state routine */
	
	TIFFFieldArray*      tif_fieldscompat;
	void*            tif_clientdata;   /* callback parameter */
	uint8_t*               tif_base;         /* base of mapped file */
	TIFFUnmapFileProc    tif_unmapproc;    /* unmap file method */
};

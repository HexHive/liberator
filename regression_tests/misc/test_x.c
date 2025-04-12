#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <time.h>
#include <dirent.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <string.h>

#define SECRET_SSID "<SSID HERE>"
#define SECRET_PASS "<PASSWORD HERE>"

#define BUTTON_PIN 2
#define GREEN_PIN 4
#define RED_PIN 3
#define BUSY_PIN 5

#define INPUT_PULLUP 0x2
#define INPUT 1
#define OUTPUT 0

#define WL_CONNECTED 0xf1f1f1f1
#define WL_NO_SHIELD 0x54545454

#define HIGH 1
#define LOW 0
#define WL_IDLE_STATUS 0xffffffff

#define MP3_IDLE 0
#define MP3_PLAY 1
#define MP3_PAUSE 2
#define MP3_LOAD 3

typedef struct mp3{
  int status;
  int freq;
  int volume;
  char buf[200];
  char path[100];
  char song_name[40];
}mp3_t;

void myDFPlayer_play(mp3_t *mp3) {

  char fake_write_reg;

  printf("*** open: %s ***\n", mp3->path);

  FILE *f = fopen(mp3->path, "rb");
  if (f == NULL)
    exit(0);

  int c = 100;
  int i = 0;
  while(c > 0x20){
      c = fgetc(f);
      mp3->buf[i] = c;
      i++;
  }
  fclose(f);

  printf("*** play ***\n");

  for(int i = 0; i < 1024; i++){
    fake_write_reg += mp3->buf[i] % 10000;
    fake_write_reg = fake_write_reg *4;
  }

  printf("*** play finish ***\n");
}

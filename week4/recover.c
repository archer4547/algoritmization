#include <stdio.h>
#include <stdint.h>

int main(int argc, char *argv[])
{
    if (argc != 2) // check if number of command line arguments is 2
    {
        printf("usage: ./recover file_namr\n");
        return 1;
    }

    FILE *card = fopen(argv[1], "r"); // open card
    if (card == NULL) // check if card exists
    {
        fclose(card);
        printf("can`t open the file\n");
        return 1;
    }

    uint8_t FAT_block[512];
    int count = 0;
    char jpeg_name[8] = "000.jpg";
    FILE *jpeg = NULL;

    while (fread(FAT_block, 1, 512, card))
    {
        if (FAT_block[0] == 0xff && FAT_block[1] == 0xd8 && FAT_block[2] == 0xff && (FAT_block[3] & 0xf0) == 0xe0)
        {
            if (count == 0)
            {
                jpeg = fopen(jpeg_name, "w");
                fwrite(FAT_block, 1, 512, jpeg);
            }
            else
            {
                fclose(jpeg);
                sprintf(jpeg_name, "%03i.jpg", count);
                jpeg = fopen(jpeg_name, "w");
                fwrite(FAT_block, 1, 512, jpeg);
            }
            count++;
        }
        else if (count != 0)
        {
            fwrite(FAT_block, 1, 512, jpeg);
        }
    }
    fclose(card); // close card
    fclose(jpeg); // close last jpeg
}

#include "helpers.h"
#include <math.h>
#include <cs50.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    int average;
    float avg = 3;
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            average = round((image[i][j].rgbtRed + image[i][j].rgbtGreen + image[i][j].rgbtBlue) / avg); // calculate average of 3 colours
            image[i][j].rgbtRed = image[i][j].rgbtGreen = image[i][j].rgbtBlue = average; // setting pixel colour to their gray format
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE temp;
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width / 2; j++)
        {
            temp = image[i][j];
            image[i][j] = image[i][width - 1 - j];
            image[i][width - 1 - j] = temp;
        }
    }
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    float average = 0;
    bool exist[3][3];
    int red, green, blue;
    RGBTRIPLE img[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // setting value of every element of "exist" to true
            for (int n = 0; n < 3; n++)
            {
                for (int k = 0; k < 3; k++)
                {
                    exist[n][k] = true;
                }
            }

            // elements that are not pixels are false
            if (i == 0)
            {
                exist[0][0] = exist[0][1] = exist[0][2] = false;
            }
            if (i == height - 1)
            {
                exist[2][0] = exist[2][1] = exist[2][2] = false;
            }
            if (j == 0)
            {
                exist[0][0] = exist[1][0] = exist[2][0] = false;
            }
            if (j == width - 1)
            {
                exist[0][2] = exist[1][2] = exist[2][2] = false;
            }

            // sum of R, G and B
            red = green = blue = average = 0;
            for (int n = 0; n < 3; n++)
            {
                for (int k = 0; k < 3; k++)
                {
                    if (exist[n][k])
                    {
                        red += image[i - (1 - n)][j - (1 - k)].rgbtRed;
                        green += image[i - (1 - n)][j - (1 - k)].rgbtGreen;
                        blue += image[i - (1 - n)][j - (1 - k)].rgbtBlue;
                        average++;
                    }
                }
            }

            // changing pixel colour but not on the main picture
            img[i][j].rgbtRed = round(red / average);
            img[i][j].rgbtGreen = round(green / average);
            img[i][j].rgbtBlue = round(blue / average);
        }
    }

    // changing pixels of main piture
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j].rgbtRed = img[i][j].rgbtRed;
            image[i][j].rgbtGreen = img[i][j].rgbtGreen;
            image[i][j].rgbtBlue = img[i][j].rgbtBlue;
        }
    }
    return;
}

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    bool exist[3][3];
    int red = 0, green = 0, blue = 0;
    RGBTRIPLE img[height][width];
    RGBTRIPLE grid[3][3]; // useful for finding gx and gy
    int gx_red, gx_green, gx_blue, gy_red, gy_green, gy_blue, final_red, final_green, final_blue;
    int gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}}; // gx "kernel"
    int gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}}; // gy "kernel"
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // setting value of every element of "exist" to true
            for (int n = 0; n < 3; n++)
            {
                for (int k = 0; k < 3; k++)
                {
                    exist[n][k] = true;
                }
            }

            // elements that are not pixels are false
            if (i == 0)
            {
                exist[0][0] = exist[0][1] = exist[0][2] = false;
            }
            if (i == height - 1)
            {
                exist[2][0] = exist[2][1] = exist[2][2] = false;
            }
            if (j == 0)
            {
                exist[0][0] = exist[1][0] = exist[2][0] = false;
            }
            if (j == width - 1)
            {
                exist[0][2] = exist[1][2] = exist[2][2] = false;
            }

            // setting value for grid that will be later multiplied by gx and gy
            for (int n = 0; n < 3; n++)
            {
                for (int k = 0; k < 3; k++)
                {
                    if (exist[n][k])
                    {
                        grid[n][k].rgbtRed = image[i - (1 - n)][j - (1 - k)].rgbtRed;
                        grid[n][k].rgbtGreen = image[i - (1 - n)][j - (1 - k)].rgbtGreen;
                        grid[n][k].rgbtBlue = image[i - (1 - n)][j - (1 - k)].rgbtBlue;
                    }
                    else
                    {
                        grid[n][k].rgbtRed = grid[n][k].rgbtGreen = grid[n][k].rgbtBlue = 0;
                    }
                }
            }

            // sum of elements of (grid * gx) and (grind * gy)
            gx_red = gx_green = gx_blue = gy_red = gy_green = gy_blue = final_red = final_green = final_blue = 0;
            for (int n = 0; n < 3; n++)
            {
                for (int k = 0; k < 3; k++)
                {
                    gx_red += gx[n][k] * grid[n][k].rgbtRed;
                    gy_red += gy[n][k] * grid[n][k].rgbtRed;
                    gx_green += gx[n][k] * grid[n][k].rgbtGreen;
                    gy_green += gy[n][k] * grid[n][k].rgbtGreen;
                    gx_blue += gx[n][k] * grid[n][k].rgbtBlue;
                    gy_blue += gy[n][k] * grid[n][k].rgbtBlue;
                }
            }

            // final value of the sobel algorithm
            final_red = round(sqrt(pow(gx_red, 2) + pow(gy_red, 2)));
            final_green = round(sqrt(pow(gx_green, 2) + pow(gy_green, 2)));
            final_blue = round(sqrt(pow(gx_blue, 2) + pow(gy_blue, 2)));

            // setting value of number to 255 if final colour > 255
            if (final_red > 255)
            {
                final_red = 255;
            }
            if (final_green > 255)
            {
                final_green = 255;
            }
            if (final_blue > 255)
            {
                final_blue = 255;
            }

            // changing pixel colour but not on the main picture
            img[i][j].rgbtRed = final_red;
            img[i][j].rgbtGreen = final_green;
            img[i][j].rgbtBlue = final_blue;
        }
    }

    // changing pixels of main piture
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j].rgbtRed = img[i][j].rgbtRed;
            image[i][j].rgbtGreen = img[i][j].rgbtGreen;
            image[i][j].rgbtBlue = img[i][j].rgbtBlue;
        }
    }
    return;
}

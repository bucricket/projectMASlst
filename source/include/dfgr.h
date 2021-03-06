/****************************************************************************
 * NCSA HDF                                                                 *
 * Software Development Group                                               *
 * National Center for Supercomputing Applications                          *
 * University of Illinois at Urbana-Champaign                               *
 * 605 E. Springfield, Champaign IL 61820                                   *
 *                                                                          *
 * For conditions of distribution and use, see the accompanying             *
 * hdf/COPYING file.                                                        *
 *                                                                          *
 ****************************************************************************/

/* $Id: dfgr.h,v 1.1 2007/08/24 18:19:53 mmerritt Exp $ */

/*-----------------------------------------------------------------------------
 * File:    dfgr.h
 * Purpose: header file for the Raster Image set
 * Invokes: df.h
 * Contents:
 *  Structure definitions: DFGRdr, DFGRrig
 * Remarks: This is included with user programs which use general raster
 *---------------------------------------------------------------------------*/

#ifndef DFGR_H  /* avoid re-inclusion */
#define DFGR_H

/* description record: used to describe image data, palette data etc. */
typedef struct
  {
      intn        ncomponents;  /* number of components */
      intn        interlace;    /* data ordering: chunky / planar etc */
      int32       xdim;         /* X- dimension of data */
      int32       ydim;         /* Y- dimensionsof data */
      DFdi        nt;           /* number type of data */
      DFdi        compr;        /* compression */
      /* ### Note: compression is currently uniquely described with a tag.
         No data is attached to this tag/ref.  But this capability is
         provided for future expansion, when this tag/ref might point to
         some data needed for decompression, such as the actual encodings */
  }
DFGRdr;

/* structure to hold RIG info */
typedef struct
  {
      char       *cf;           /* color format */
      int32       xpos;         /* X position of image on screen */
      int32       ypos;         /* Y position of image on screen */
      float32     aspectratio;  /* ratio of pixel height to width */
      float32     ccngamma;     /* gamma color correction parameter */
      float32     ccnred[3];    /* red color correction parameter */
      float32     ccngrren[3];  /* green color correction parameter */
      float32     ccnblue[3];   /* blue color correction parameter */
      float32     ccnwhite[3];  /* white color correction parameter */
      DFdi        data[3];      /* image/lut/mattechannel */
      DFGRdr      datadesc[3];  /* description of image/lut/mattechannel */
  }
DFGRrig;

#if defined c_plusplus || defined __cplusplus
extern      "C"
{
#endif                          /* c_plusplus || __cplusplus */

/* Library-developer functions */
    extern int32 DFGRIopen
                (const char *filename, int acc_mode);

#if defined c_plusplus || defined __cplusplus
}
#endif                          /* c_plusplus || __cplusplus */

#endif                          /* DFGR_H */

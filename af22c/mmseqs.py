"""
This file contains code for calling mmseqs from our framework to calculate Neff
scores. Call `neff` from the base module with mode set to mmseqs to use this
functionality.
"""

import os
import subprocess as sp
import sys
import struct
from tempfile import TemporaryDirectory
from .utils import as_handle
from typing import Union

def mmseqs_neff_from_a3m(
  a3m_file_or_path,
  mmseqs: str = "mmseqs",
  mmseqs_flags: Union[dict[str,str],dict[str,list[str]]] = None
):
  """
  Generate Neff scores from a .a3m file with mmseqs.
  
  Args:
    a3m_file_path: something (path/file handle) that can be used as a file
    mmseqs: path to the mmseqs executable
    mmseqs_flags: specify flags for each stage of calling mmseqs, therefore this
      parameter is expected as a dictionary mapping from a pipeline step (either
      "msa2profile" and/or "profile2neff") to a str or a list of strs containing
      command-line parameters. Note that no proper escaping is done, therefore
      mmseqs_flags may be exploited to issue arbitrary console commands.
  
  Return:
    A list of Neff scores generated by mmseqs.
  """
  # parse flags
  if mmseqs_flags is not None:
    mmseqs_flags = {
      # join list[str] to space-seperated str if not already str'ed
      k: " " + (v if isinstance(v,str) else " ".join(v))
      for k, v in mmseqs_flags.items()
    }
  else:
    mmseqs_flags = {}
  msa2profile_flags = mmseqs_flags.get("msa2profile", "")
  profile2neff_flags = mmseqs_flags.get("profile2neff", "")

  # call mmseqs
  with as_handle(a3m_file_or_path) as a3m_handle:
    with TemporaryDirectory() as tempdir:
      infile = a3m_handle.read()
      
      # this hack creates a valid mmseqs db from a single .a3m file in 3 steps
      # (by default mmseqs cannot use .a3m files as db input)
      # 1) copy original a3m file and append a null byte
      dbfilename = os.path.join(tempdir,"msaDb")
      with open(dbfilename, "wb") as dbfile:
        dbfile.write(infile.encode())
        dbfile.write(struct.pack("B", 0))
      # 2) write a .dbtype file specifying 0xb = 0d11 as mode, which indicates a3m
      with open(f"{dbfilename}.dbtype", "wb") as dbtype:
        dbtype.write(struct.pack("<Bxxx", 0xb))
      # 3) write a .index file specifying a single entry
      with open(f"{dbfilename}.index", "w") as dbindex:
        size = len(infile)  # write size of ORIGINAL file
        dbindex.write("\t".join(["0", "0", str(size)]) + "\n")
      
      # create an mmseqs profile
      profile_filename = os.path.join(tempdir,"profileDb")
      profileret = sp.run(
        "%s msa2profile %s %s%s" % (
          mmseqs, dbfilename, profile_filename, msa2profile_flags
        ),
        shell=True,stdout=sp.PIPE,stderr=sp.PIPE,
      )
      if profileret.returncode != 0:
        raise RuntimeError(
          f"failed to convert MSA to profile.\n"
          f"cmd stdout:\n{profileret.stdout.decode()}\n"
          f"cmd stderr:\n{profileret.stderr.decode()}"
        )
      
      # compute Neff scores
      mmseqs_neff_filename = os.path.join(tempdir,"neff.txt")
      neffret = sp.run(
        "%s profile2neff %s %s%s" % (
          mmseqs, profile_filename, mmseqs_neff_filename, profile2neff_flags
        ),
        shell=True,stdout=sp.PIPE,stderr=sp.PIPE,
      )
      if neffret.returncode != 0:
        raise RuntimeError(
          f"failed to extract Neff scores from profileDb.\n"
          f"cmd stdout:\n{profileret.stdout.decode()}\n"
          f"cmd stderr:\n{profileret.stderr.decode()}"
        )
      
      # extract Neff scores from first line of output
      # TODO: handle multiple sequences in one .a3m file!
      return [
        float(f) for f in open(mmseqs_neff_filename).read().splitlines()[1].split("\t")
      ]


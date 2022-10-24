# SACMES

[![CodeFactor](https://www.codefactor.io/repository/github/paradoxdruid/SACMES/badge)](https://www.codefactor.io/repository/github/paradoxdruid/SACMES) [![CodeQL](https://github.com/Paradoxdruid/SACMES/actions/workflows/codeql.yml/badge.svg)](https://github.com/Paradoxdruid/SACMES/actions/workflows/codeql.yml) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) ![License: MIT](https://img.shields.io/badge/license-MIT-green)

**SACMES** stands for **S**oftware for the **A**nalysis and **C**ontinuous **M**onitoring of **E**lectrochemical **S**ystems. These scripts analyzes data from specific electrochemical techniques in real time and export the data into space delimited txt files. Each script runs off of an multithreaded animation module known as ElectrochemicalAnimation and can analyze any number of electrodes simultaneously.

<hr />

## Status & Goals

This cloned repository was created to allow refactoring of SACMES into a module format, as well as to enable SACMES to read WaveNano potentiostat files.   Work in progress.

Original repository available at: <https://github.com/netzlab/SACMES>

## sacmes module

This python module version of SACMES allows analysis of data from Square-Wave Voltammograms and offers real time control of data analysis.  **This is the up to date code of this repository.**

Usage: `python sacmes`

## Published Versions of SACMES

If you would like to use the SACMES program as it is described in the ACS Analytical Chemistry article "Open Source Software for the Real-Time Control, Processing, and Visualization of High-Volume Electrochemical Data" by Curtis, et al. use the scripts within the "Published Versions of SACMES" folder.

All updates for the Standard Operating Procedure (SOP) can be viewed here: <https://www.dropbox.com/sh/5s7qxgzpmx6pnq4/AACC3I0DrIL22cUM8fk1RC01a?dl=0>

## Old Versions of SACMES

This folder has cleaned up but largely unchanged SACMES scripts.

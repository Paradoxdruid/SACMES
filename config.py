# globals

from dataclasses import dataclass
from typing import List, Dict, Any
import tkinter as tk
import matplotlib.pyplot as plt


@dataclass
class Config:
    # File data
    encoding: str = "utf-16"
    container: tk.Frame
    Plot: str = "unused"  # TODO: Unused

    HighLowList: Dict[str, int]
    delimiter: int
    extension: str = ".csv"

    # Tkinter Frames
    frame_list: List[tk.Frame]
    PlotValues: List[tk.Frame]
    ShowFrames: Dict[str, tk.Frame]

    # Current Data Values
    current_column: int = 1
    current_column_index: int = 0
    voltage_column: int = 1
    voltage_column_index: int = 0
    spacing_index: int = 3
    total_columns: int
    byte_limit: int = 3000
    byte_index: int = 2
    figures: List[plt.Plot]
    StartNormalizationVar: str = "unused"  # TODO: unused
    SaveBox: str = "unused"  # TODO: unused
    ManipulateFrequenciesFrame: tk.Frame
    InputFrequencies: List[int] = [30, 80, 240]
    e_var: str = "single"
    FilePath: str = ""
    ExportPath: str = ""
    FoundFilePath: bool
    DataFolder: str
    method: str = ""
    SelectedOptions: str = ""
    XaxisOptions: str = ""
    electrode_count: int = 0
    electrode_list: List[int]
    electrode_dict: Dict[int, int]
    frequency_list: List[int]
    frequency_dict: Dict[int, int]
    LowFrequency: int
    HighFrequency: int
    HighLowList: Dict[str, int]
    mypath: str
    Option: str  # TODO: just a reference to SelectedOptions
    FileHandle: str
    ExportFilePath: str
    AlreadyInitiated: bool
    FileHandle: str
    starting_file: int = 1
    post_analysis: tk.Frame
    handle_variable: str = ""
    track: Any  # TODO: Track class seems like an odd wrapper for updating lists
    Interval: int
    PlotContainer: tk.Frame
    data_normalization: Any  # TODO: awkward wrapper for updating normalization
    resize_interval: int
    InjectionPoint: int
    InjectionVar: bool
    ratio_min
    ratio_max
    min_norm
    max_norm
    min_raw
    max_raw
    min_data
    max_data
    InitializedNormalization
    RatioMetricCheck
    NormWarningExists
    NormalizationVault
    wait_time
    SaveVar
    track
    numFiles
    SampleRate
    ratiometricanalysis
    frames
    generate
    Plot
    anim
    NormalizationPoint
    q
    wait_time
    track
    initialize
    LowFrequencyEntry
    high_xstart_entry
    low_xstart_entry
    high_xend_entry
    low_xend_entry
    HighFrequencyEntry
    NormWarning
    FileLabel
    RealTimeSampleLabel
    SetPointNorm
    NormalizationVar
    low_xstart
    high_xstart
    low_xend
    high_xend
    sg_window
    LowFrequencyOffset
    LowFrequencySlope
    ExistVar
    WrongFrequencyLabel
    analysis_complete
    key
    PoisonPill
    LowAlreadyReset
    HighAlreadyReset
    extrapolate
    AlreadyReset
    FrameFileLabel: tk.Label
    text_file_export
    offset_normalized_data_list
    FrameReference
    KDM_List
    empty_ratiometric_plots
    empty_ratiometric_plots
    ratiometric_figures
    normalized_ratiometric_data_list
    normalized_data_list
    frequency_list
    data_list
    plot_list
    EmptyPlots
    sample_list
    PlotFrames
    list_val
    EmptyRatioPlots
    peak
    norm
    NormalizationWaiting

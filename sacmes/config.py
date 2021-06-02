#!/usr/bin/env python3

from typing import List, Dict, Any, Tuple
import tkinter as tk
from queue import Queue
import tkinter.ttk as ttk


class Config:
    """Class to store SACMES values and frames."""

    # File data
    encoding: str = None
    handle_variable: str = ""

    HighLowList: Dict[str, int] = None

    # Tkinter Frames
    root: tk.Tk = None
    frame_list: List[tk.Frame] = None
    PlotValues: List[tk.Frame] = None
    ShowFrames: Dict[str, tk.Frame] = None
    container: tk.Frame = None

    # Styling
    HUGE_FONT: Tuple[str, int] = ("Verdana", 18)
    LARGE_FONT: Tuple[str, int] = ("Verdana", 11)
    MEDIUM_FONT: Tuple[str, int] = ("Verdnana", 10)
    SMALL_FONT: Tuple[str, int] = ("Verdana", 8)

    # Regression Parameters
    sg_window: int = 5
    polyfit_deg: int = 15
    sg_degree: int = 1
    cutoff_frequency: int = 50

    # Checkpoint parameters
    key: int = 0
    PoisonPill: bool = False
    FoundFilePath: bool = False
    ExistVar: bool = False
    AlreadyInitiated: bool = False
    LowAlreadyReset: bool = False
    HighAlreadyReset: bool = False
    analysis_complete: bool = False

    # Data extraction parameters
    delimiter: int = 1
    extension: str = 1
    current_column: int = 4
    current_column_index: int = 3
    voltage_column: int = 1
    voltage_column_index: int = 0
    spacing_index: int = 3
    byte_limit: int = 3000
    byte_index: int = 2

    # Low frequency baseline parameters
    LowFrequencyOffset: float = 0
    LowFrequencySlope: float = 0

    # Current Data Values

    total_columns: int = None

    figures: List[Any] = None
    ManipulateFrequenciesFrame: tk.Frame = None
    InputFrequencies: List[int] = [30, 80, 240]
    e_var: str = "single"
    FilePath: str = None
    ExportPath: str = None

    DataFolder: str = None
    method: str = None
    SelectedOptions: str = None
    XaxisOptions: str = None
    electrode_count: int = None
    electrode_list: List[int] = None
    electrode_dict: Dict[int, int] = None
    frequency_list: List[int] = None
    frequency_dict: Dict[int, int] = None
    electrodes: List[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    LowFrequency: int = None
    HighFrequency: int = None
    HighLowList: Dict[str, int] = None
    mypath: str = None
    Option: str = None  # just a reference to SelectedOptions
    FileHandle: str = None
    ExportFilePath: str = None

    starting_file: int = None
    post_analysis: tk.Frame = None
    track: Any = None  # Track class seems like an odd wrapper for updating lists
    Interval: int = None
    PlotContainer: tk.Frame = None
    data_normalization: Any = None  # awkward wrapper for updating normalization
    resize_interval: int = None
    InjectionPoint: int = None
    InjectionVar: bool = None
    ratio_min: float = None
    ratio_max: float = None
    min_norm: float = None
    max_norm: float = None
    min_raw: float = None
    max_raw: float = None
    min_data: float = None
    max_data: float = None
    InitializedNormalization: bool = None
    RatioMetricCheck: bool = None
    NormWarningExists: bool = None
    NormalizationVault: List[int] = None
    wait_time: Any = None  # class wrapper for updating noralization status
    SaveVar: bool = None
    numFiles: int = None
    SampleRate: float = None

    anim: List[Any] = None
    NormalizationPoint: int = None
    q: Queue = None
    initialize: Any = None  # wrapper for InitializedFrequencyMapCanvas
    LowFrequencyEntry: tk.Entry = None
    high_xstart_entry: tk.Entry = None
    low_xstart_entry: tk.Entry = None
    high_xend_entry: tk.Entry = None
    low_xend_entry: tk.Entry = None
    HighFrequencyEntry: tk.Entry = None
    NormWarning: tk.Label = None
    FileLabel: ttk.Label = None
    RealTimeSampleLabel: ttk.Label = None
    SetPointNorm: ttk.Entry = None
    NormalizationVar: tk.StringVar = None
    low_xstart: float = None
    high_xstart: float = None
    low_xend: float = None
    high_xend: float = None

    WrongFrequencyLabel: tk.Label = None

    AlreadyReset: bool = None
    FrameFileLabel: tk.Label = None
    text_file_export: Any = None
    offset_normalized_data_list: List[int] = None
    FrameReference: Any = None
    KDM_list: List[Any] = None

    ratiometric_plots: List[Any] = None
    ratiometric_figures: List[Any] = None
    normalized_ratiometric_data_list: List[float] = None
    normalized_data_list: List[Any] = None
    data_list: List[Any] = None
    plot_list: List[Any] = None
    EmptyPlots: List[Any] = None
    sample_list: List[float] = None
    PlotFrames: Dict[tk.Frame, Any] = None
    list_val: int = None
    EmptyRatioPlots: List[Any] = None
    peak: Any = None
    norm: Any = None
    NormalizationWaiting: bool = None
    file_list: List[Any] = None
    SetPointNormLabel: tk.Label = None
    root: Any = None

    # Unused
    empty_ratiometric_plots: List[Any] = None
    extrapolate: str = None
    ratiometricanalysis: str = None
    generate: str = None
    Plot: str = None
    StartNormalizationVar: str = None
    SaveBox: str = None
    Plot: str = None
    input_frame: Any = None  # store input frame


# instantiate config object to be imported by all module files
cg = Config()

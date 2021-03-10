# globals

from dataclasses import dataclass
from typing import List, Dict, Any
import tkinter as tk
import matplotlib.pyplot as plt
from queue import Queue
import tkinter.ttk as ttk


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
    ratio_min: float
    ratio_max: float
    min_norm: float
    max_norm: float
    min_raw: float
    max_raw: float
    min_data: float
    max_data: float
    InitializedNormalization: bool
    RatioMetricCheck: bool
    NormWarningExists: bool
    NormalizationVault: List[int]
    wait_time: Any  # TODO: class wrapper for updating noralization status
    SaveVar: bool
    numFiles: int
    SampleRate: float
    ratiometricanalysis: str = "unused"  # TODO: currently unused
    generate: str = "unused"  # TODO: currently unused
    Plot: str = "unused"  # TODO: currently unused
    anim: List[Any]
    NormalizationPoint: int
    q: Queue
    initialize: Any  # wrapper for InitializedFrequencyMapCanvas
    LowFrequencyEntry: tk.Entry
    high_xstart_entry: tk.Entry
    low_xstart_entry: tk.Entry
    high_xend_entry: tk.Entry
    low_xend_entry: tk.Entry
    HighFrequencyEntry: tk.Entry
    NormWarning: tk.Label
    FileLabel: ttk.Label
    RealTimeSampleLabel: ttk.Label
    SetPointNorm: ttk.Entry
    NormalizationVar: tk.StringVar
    low_xstart: float
    high_xstart: float
    low_xend: float
    high_xend: float
    sg_window: float
    LowFrequencyOffset: float
    LowFrequencySlope: float
    ExistVar: bool
    WrongFrequencyLabel: tk.Label
    analysis_complete: bool
    key: int
    PoisonPill: bool
    LowAlreadyReset: bool
    HighAlreadyReset: bool
    extrapolate: str = "unused"  # TODO: currently unused
    AlreadyReset: bool
    FrameFileLabel: tk.Label
    text_file_export: Any  # TODO: wrapper for TextFileExport
    offset_normalized_data_list: List[int]
    FrameReference: Any  # TODO: wrapper for ContinuousScanVisualizationFrame
    KDM_list: List[Any]  # TODO: looks self-referential
    empty_ratiometric_plots: List[Any]  # TODO: currently unused
    ratiometric_plots: List[Any]
    ratiometric_figures: List[Any]  # TODO: list of MakeRatioMetricFigure
    normalized_ratiometric_data_list: List[float]
    normalized_data_list: List[Any]
    frequency_list: List[int]
    data_list: List[Any]
    plot_list: List[Any]
    EmptyPlots: List[Any]
    sample_list: List[float]
    PlotFrames: Dict[
        tk.Frame, Any
    ]  # TODO: this is messy, looks like frames as key and value
    list_val: int
    EmptyRatioPlots: List[Any]
    peak: Any  # TODO: pyplot plot?
    norm: Any  # TODO: pyplot plot?
    NormalizationWaiting: bool

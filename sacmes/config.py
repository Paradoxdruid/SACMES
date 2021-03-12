# globals

# from dataclasses import dataclass
from typing import List, Dict, Any
import tkinter as tk
from queue import Queue
import tkinter.ttk as ttk


# @dataclass
class Config:
    # File data
    encoding: str = None
    container: Any = None
    Plot: str = None  # TODO: Unused

    HighLowList: Dict[str, int] = None
    delimiter: int = None
    extension: str = None

    # Tkinter Frames
    frame_list: List[tk.Frame] = None
    PlotValues: List[tk.Frame] = None
    ShowFrames: Dict[str, tk.Frame] = None

    # Current Data Values
    current_column: int = None
    current_column_index: int = None
    voltage_column: int = None
    voltage_column_index: int = None
    spacing_index: int = None
    total_columns: int = None
    byte_limit: int = None
    byte_index: int = None
    figures: List[Any] = None
    StartNormalizationVar: str = None  # TODO: unused
    SaveBox: str = None  # TODO: unused
    ManipulateFrequenciesFrame: tk.Frame = None
    InputFrequencies: List[int] = [30, 80, 240]
    e_var: str = "single"
    FilePath: str = None
    ExportPath: str = None
    FoundFilePath: bool = False
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
    Option: str = None  # TODO: just a reference to SelectedOptions
    FileHandle: str = None
    ExportFilePath: str = None
    AlreadyInitiated: bool = False
    starting_file: int = None
    post_analysis: tk.Frame = None
    handle_variable: str = ""
    track: Any = None  # TODO: Track class seems like an odd wrapper for updating lists
    Interval: int = None
    PlotContainer: tk.Frame = None
    data_normalization: Any = None  # TODO: awkward wrapper for updating normalization
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
    wait_time: Any = None  # TODO: class wrapper for updating noralization status
    SaveVar: bool = None
    numFiles: int = None
    SampleRate: float = None
    ratiometricanalysis: str = None  # TODO: currently unused
    generate: str = None  # TODO: currently unused
    Plot: str = None  # TODO: currently unused
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
    sg_window: int = 5
    LowFrequencyOffset: float = None
    LowFrequencySlope: float = None
    ExistVar: bool = False
    WrongFrequencyLabel: tk.Label = None
    analysis_complete: bool = None
    key: int = 0
    PoisonPill: bool = False
    LowAlreadyReset: bool = None
    HighAlreadyReset: bool = None
    extrapolate: str = None  # TODO: currently unused
    AlreadyReset: bool = None
    FrameFileLabel: tk.Label = None
    text_file_export: Any = None  # TODO: wrapper for TextFileExport
    offset_normalized_data_list: List[int] = None
    FrameReference: Any = None  # TODO: wrapper for ContinuousScanVisualizationFrame
    KDM_list: List[Any] = None  # TODO: looks self-referential
    empty_ratiometric_plots: List[Any] = None  # TODO: currently unused
    ratiometric_plots: List[Any] = None
    ratiometric_figures: List[Any] = None  # TODO: list of MakeRatioMetricFigure
    normalized_ratiometric_data_list: List[float] = None
    normalized_data_list: List[Any] = None
    data_list: List[Any] = None
    plot_list: List[Any] = None
    EmptyPlots: List[Any] = None
    sample_list: List[float] = None
    PlotFrames: Dict[
        tk.Frame, Any
    ] = None  # TODO: this is messy, looks like frames as key and value
    list_val: int = None
    EmptyRatioPlots: List[Any] = None
    peak: Any = None  # TODO: pyplot plot?
    norm: Any = None  # TODO: pyplot plot?
    NormalizationWaiting: bool = None
    file_list: List[Any] = None
    SetPointNormLabel: tk.Label = None
    cutoff_frequency: int = 50
    polyfit_deg: int = 15
    sg_degree: int = 1
    root: Any = None


cg = Config()

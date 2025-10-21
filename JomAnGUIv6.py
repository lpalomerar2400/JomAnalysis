import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import os
from matplotlib.figure import Figure
import glob
from datetime import datetime

# =============================================================================
# CHANGE CONTROL CHART - JOMINY ANALYZER DEVELOPMENT
# =============================================================================
"""
VERSION HISTORY:
-------------------------------------------------------------------------------
v1.0 - BASE VERSION
- Initial Jominy analysis script with basic functionality
- S-G smoothing, t8/5 calculation, cooling rate analysis
- Excel file input/output

v2.0 - GUI IMPLEMENTATION  
- Added tkinter GUI for user-friendly operation
- File browsing, column selection, parameter adjustment
- Basic plotting capabilities

v3.0 - DEBUGGING & ERROR HANDLING
- Enhanced data validation and error reporting
- Data inspection tools
- Robust handling of edge cases and invalid data

v4.0 - INTERACTIVE CHARTS & PNG EXPORT
- Separate chart windows with navigation toolbars
- Zoom, pan, reset functionality
- PNG-only image export (removed JPEG/BMP due to issues)

v5.0 - BATCH PROCESSING
- Multi-file batch analysis capability
- Progress tracking and error reporting
- Batch results summary and export

v6.0 - ENHANCED COOLING ANALYSIS & TXT EXPORT
- Average and lowest cooling rate within t8/5 range
- Time tracking for minimum cooling rate
- TXT export with automatic naming
- Comprehensive reporting

v7.0 - FINAL VERSION (CURRENT)
- Integrated change control documentation
- Version tracking in GUI
- All previous features maintained and optimized
-------------------------------------------------------------------------------
"""

class JominyDebugAnalyzer:
    # Version information
    VERSION = "v7.0"
    VERSION_DATE = "2025-20-10"
    RELEASE_NOTES = """
    Final Version - Integrated Change Control
    • All v1-v6 features maintained
    • Added version tracking and documentation
    • Enhanced stability and performance
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"Jominy Test Analyzer - {self.VERSION}")
        self.root.geometry("1200x900")
        
        self.df = None
        self.results = {}
        self.figures = {}  # Store figures for saving
        self.batch_results = {}  # Store batch processing results
        self.current_filename = None  # Track current file name
        
        self.setup_gui()
        
    def setup_gui(self):
        """Create the GUI layout with debug features"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Version info frame
        version_frame = ttk.Frame(main_frame)
        version_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(version_frame, text=f"Version: {self.VERSION} - {self.VERSION_DATE}", 
                 font=('Arial', 9, 'bold'), foreground='blue').pack(side=tk.LEFT)
        ttk.Button(version_frame, text="View Change Log", 
                  command=self.show_change_log, width=15).pack(side=tk.RIGHT)
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="1. File Selection & Data Inspection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(file_frame, text="Browse Excel File", 
                  command=self.browse_file).grid(row=0, column=0, padx=5)
        ttk.Button(file_frame, text="Batch Process Files", 
                  command=self.batch_process_files).grid(row=0, column=1, padx=5)
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.grid(row=0, column=2, padx=5)
        
        ttk.Button(file_frame, text="Inspect Data", 
                  command=self.inspect_data).grid(row=0, column=3, padx=5)
        
        # Column selection section
        self.column_frame = ttk.LabelFrame(main_frame, text="2. Column Selection", padding="10")
        self.column_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.column_frame, text="Time Column:").grid(row=0, column=0, padx=5)
        self.time_combo = ttk.Combobox(self.column_frame, state="readonly", width=20)
        self.time_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(self.column_frame, text="Temperature Column:").grid(row=0, column=2, padx=5)
        self.temp_combo = ttk.Combobox(self.column_frame, state="readonly", width=20)
        self.temp_combo.grid(row=0, column=3, padx=5)
        
        # Analysis parameters section
        param_frame = ttk.LabelFrame(main_frame, text="3. Analysis Parameters", padding="10")
        param_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(param_frame, text="S-G Window:").grid(row=0, column=0, padx=5)
        self.window_entry = ttk.Entry(param_frame, width=10)
        self.window_entry.insert(0, "11")
        self.window_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(param_frame, text="S-G Polynomial:").grid(row=0, column=2, padx=5)
        self.poly_entry = ttk.Entry(param_frame, width=10)
        self.poly_entry.insert(0, "3")
        self.poly_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(param_frame, text="Cooling Rate Threshold:").grid(row=0, column=4, padx=5)
        self.threshold_entry = ttk.Entry(param_frame, width=10)
        self.threshold_entry.insert(0, "1.0")
        self.threshold_entry.grid(row=0, column=5, padx=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Run Analysis", 
                  command=self.run_analysis).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Debug Data", 
                  command=self.debug_data).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Plot Results", 
                  command=self.plot_results).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Save Charts", 
                  command=self.save_charts).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Save Results", 
                  command=self.save_results).grid(row=0, column=4, padx=5)
        ttk.Button(button_frame, text="View Batch Results", 
                  command=self.view_batch_results).grid(row=0, column=5, padx=5)
        ttk.Button(button_frame, text="Export to TXT", 
                  command=self.export_to_txt).grid(row=0, column=6, padx=5)
        
        # Data info display
        info_frame = ttk.LabelFrame(main_frame, text="Data Inspection", padding="10")
        info_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.info_text = tk.Text(info_frame, height=12, width=100)
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Results display
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        results_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.results_text = tk.Text(results_frame, height=8, width=100)
        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
    
    def show_change_log(self):
        """Display the change control chart"""
        change_log = """
JOMINY ANALYZER - CHANGE CONTROL CHART
=======================================

AUTHOR INFORMATION:
-------------------
• Developer: [Luis Rodrigo Palomera, A240619]
• Institution: [Instituto Politécnico Nacional (IPN)] 
• Department: [CICATA Queretaro]
• Project: [CVU 881822]
• GitHub: [lpalomerar2400]

CONTACT:
--------
• Email: [palomera.luis@gmail.com]
• Project Repository: [https://github.com/lpalomerar2400/JomAnalysis]

VERSION v7.0 - FINAL VERSION
-----------------------------
• Integrated change control documentation
• Version tracking in GUI
• All previous features maintained and optimized

VERSION v6.0 - ENHANCED COOLING ANALYSIS & TXT EXPORT
-----------------------------------------------------
• Average cooling rate within t8/5 range
• Lowest cooling rate within t8/5 range  
• Time tracking for minimum cooling rate
• TXT export with automatic naming
• Comprehensive reporting format

VERSION v5.0 - BATCH PROCESSING
--------------------------------
• Multi-file batch analysis capability
• Progress tracking with real-time updates
• Batch results summary and comparison
• Export all results to single Excel file
• Error handling for individual file failures

VERSION v4.0 - INTERACTIVE CHARTS & PNG EXPORT
-----------------------------------------------
• Separate chart windows for each plot
• Matplotlib navigation toolbars (zoom, pan, reset)
• PNG-only export (removed problematic JPEG/BMP)
• Individual chart save buttons
• Enhanced visualization quality

VERSION v3.0 - DEBUGGING & ERROR HANDLING
------------------------------------------
• Comprehensive data validation
• Detailed error reporting and warnings
• Data inspection tools
• Robust handling of edge cases
• Improved user feedback

VERSION v2.0 - GUI IMPLEMENTATION
----------------------------------
• Tkinter-based user interface
• File browsing and column selection
• Parameter adjustment controls
• Basic plotting capabilities
• Excel input/output integration

VERSION v1.0 - BASE VERSION
----------------------------
• Core Jominy analysis algorithms
• S-G smoothing filter implementation
• t8/5 time calculation
• Cooling rate analysis
• Phase change detection
• Excel file processing

DEVELOPMENT NOTES:
• All versions maintain backward compatibility
• Each version builds upon previous functionality
• Error handling improved with each iteration
• User experience enhanced throughout development
• Developed as part of academic research in materials science

ACKNOWLEDGMENTS:
• Thanks to the open-source community for pandas, numpy, scipy, and matplotlib
• Special thanks to academic advisors and research colleagues
"""
        log_window = tk.Toplevel(self.root)
        log_window.title("Change Control Chart - Version History")
        log_window.geometry("800x600")
        
        text_widget = tk.Text(log_window, wrap=tk.WORD, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(log_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.insert(tk.END, change_log)
        text_widget.config(state=tk.DISABLED)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    
    def browse_file(self):
        """Browse for Excel file"""
        filename = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if filename:
            self.current_filename = filename
            self.file_label.config(text=os.path.basename(filename))
            self.load_file(filename)
    
    def batch_process_files(self):
        """Batch process multiple Excel files"""
        files = filedialog.askopenfilenames(
            title="Select Excel Files for Batch Processing",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if not files:
            return
        
        # Ask for column selection if this is the first file
        if self.df is None and files:
            test_df = pd.read_excel(files[0])
            self.show_column_selection_dialog(test_df.columns.tolist())
        
        # Get analysis parameters
        try:
            window_length = int(self.window_entry.get())
            polyorder = int(self.poly_entry.get())
            cooling_threshold = float(self.threshold_entry.get())
        except:
            messagebox.showerror("Error", "Invalid analysis parameters!")
            return
        
        # Process files
        self.batch_results.clear()
        success_count = 0
        error_files = []
        
        progress_window = self.create_progress_window(len(files))
        
        for i, filename in enumerate(files):
            try:
                # Update progress
                self.update_progress(progress_window, i, len(files), f"Processing: {os.path.basename(filename)}")
                
                # Load and analyze file
                df = pd.read_excel(filename)
                time_col = self.time_combo.get()
                temp_col = self.temp_combo.get()
                
                analyzer = JominyAnalyzer(df, time_col, temp_col)
                results = analyzer.analyze_all_curves(window_length, polyorder, cooling_threshold)
                
                # Store results with filename as key
                self.batch_results[os.path.basename(filename)] = {
                    'results': results,
                    'full_path': filename
                }
                success_count += 1
                
            except Exception as e:
                error_files.append((os.path.basename(filename), str(e)))
        
        # Close progress window
        progress_window.destroy()
        
        # Show results summary
        summary = f"Batch Processing Complete!\n\n"
        summary += f"Successfully processed: {success_count}/{len(files)} files\n"
        
        if error_files:
            summary += f"\nFiles with errors:\n"
            for filename, error in error_files:
                summary += f"• {filename}: {error}\n"
        
        messagebox.showinfo("Batch Processing Results", summary)
        
        # Display first file's results
        if success_count > 0:
            first_file = list(self.batch_results.keys())[0]
            self.results = self.batch_results[first_file]['results']
            self.current_filename = self.batch_results[first_file]['full_path']
            self.display_final_results()
            self.file_label.config(text=f"Batch: {first_file} (1 of {success_count})")
    
    def export_to_txt(self):
        """Export current analysis results to TXT file"""
        if not self.results:
            messagebox.showerror("Error", "Please run analysis first!")
            return
        
        if not self.current_filename:
            messagebox.showerror("Error", "No file currently loaded!")
            return
        
        try:
            # Create TXT filename based on original Excel file
            base_name = os.path.splitext(self.current_filename)[0]
            txt_filename = base_name + "_analysis_results.txt"
            
            with open(txt_filename, 'w') as f:
                f.write("JOMINY TEST ANALYSIS RESULTS\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"Data Source: {os.path.basename(self.current_filename)}\n")
                f.write(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Software Version: {self.VERSION}\n\n")
                
                f.write("KEY PARAMETERS:\n")
                f.write("-" * 30 + "\n")
                f.write(f"t8/5 Time: {self.results['t85']:.2f} seconds\n")
                f.write(f"Average Cooling Rate (Overall): {self.results['average_cooling_rate']:.2f} °C/s\n")
                f.write(f"Phase Change Time: {self.results['phase_change_time']:.2f} seconds\n")
                f.write(f"Maximum Temperature: {self.results['max_temperature']:.1f} °C\n")
                f.write(f"Minimum Temperature: {self.results['min_temperature']:.1f} °C\n")
                f.write(f"Temperature Range: {self.results['max_temperature'] - self.results['min_temperature']:.1f} °C\n\n")
                
                f.write("COOLING RATE ANALYSIS WITHIN t8/5 RANGE:\n")
                f.write("-" * 40 + "\n")
                if not np.isnan(self.results['t85_cooling_stats']['avg_cooling_rate_t85']):
                    f.write(f"Average Cooling Rate (800-500°C): {self.results['t85_cooling_stats']['avg_cooling_rate_t85']:.2f} °C/s\n")
                    f.write(f"Lowest Cooling Rate (800-500°C): {self.results['t85_cooling_stats']['min_cooling_rate_t85']:.2f} °C/s\n")
                    f.write(f"Time at Lowest Cooling Rate: {self.results['t85_cooling_stats']['time_at_min_cooling_t85']:.2f} seconds\n")
                else:
                    f.write("Cooling rate analysis within t8/5 range: Not available\n")
                f.write("\n")
                
                f.write("COOLING RATE STATISTICS (OVERALL):\n")
                f.write("-" * 40 + "\n")
                f.write(f"Maximum Cooling Rate: {self.results['cooling_rate_max']:.2f} °C/s\n")
                f.write(f"Minimum Cooling Rate: {self.results['cooling_rate_min']:.2f} °C/s\n")
                f.write(f"Standard Deviation: {self.results['cooling_rate_std']:.2f} °C/s\n\n")
                
                f.write("DATA QUALITY INFORMATION:\n")
                f.write("-" * 35 + "\n")
                f.write(f"Data Points Used: {self.results['data_points']}\n")
                f.write(f"Infinite Values in Cooling Rate: {self.results['infinite_cooling_count']}\n")
                f.write(f"NaN Values in Cooling Rate: {self.results['nan_cooling_count']}\n\n")
                
                f.write("ANALYSIS PARAMETERS:\n")
                f.write("-" * 25 + "\n")
                f.write(f"Savitzky-Golay Window: {self.window_entry.get()}\n")
                f.write(f"Savitzky-Golay Polynomial: {self.poly_entry.get()}\n")
                f.write(f"Cooling Rate Threshold: {self.threshold_entry.get()} °C/s\n")
                f.write(f"Software Version: {self.VERSION}\n")
            
            messagebox.showinfo("Success", f"Analysis results exported to:\n{txt_filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export to TXT: {str(e)}")
    
    def create_progress_window(self, total_files):
        """Create progress window for batch processing"""
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Batch Processing")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="Processing files...", font=('Arial', 12)).pack(pady=10)
        
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=self.progress_var, maximum=total_files)
        progress_bar.pack(fill=tk.X, padx=20, pady=5)
        
        self.progress_label = ttk.Label(progress_window, text="")
        self.progress_label.pack(pady=5)
        
        return progress_window
    
    def update_progress(self, progress_window, current, total, message):
        """Update progress window"""
        self.progress_var.set(current)
        self.progress_label.config(text=message)
        progress_window.update()
    
    def show_column_selection_dialog(self, columns):
        """Show dialog for column selection in batch processing"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Column Selection for Batch Processing")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Select columns for analysis:", font=('Arial', 10)).pack(pady=10)
        
        ttk.Label(dialog, text="Time Column:").pack()
        time_combo = ttk.Combobox(dialog, values=columns, state="readonly", width=30)
        time_combo.set(columns[0] if columns else "")
        time_combo.pack(pady=5)
        
        ttk.Label(dialog, text="Temperature Column:").pack()
        temp_combo = ttk.Combobox(dialog, values=columns, state="readonly", width=30)
        temp_combo.set(columns[1] if len(columns) > 1 else "")
        temp_combo.pack(pady=5)
        
        def apply_selection():
            self.time_combo.set(time_combo.get())
            self.temp_combo.set(temp_combo.get())
            dialog.destroy()
        
        ttk.Button(dialog, text="Apply", command=apply_selection).pack(pady=10)
    
    def view_batch_results(self):
        """Display batch processing results in a new window"""
        if not self.batch_results:
            messagebox.showinfo("No Batch Results", "Please run batch processing first!")
            return
        
        results_window = tk.Toplevel(self.root)
        results_window.title("Batch Processing Results Summary")
        results_window.geometry("1000x600")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(results_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Summary tab
        summary_frame = ttk.Frame(notebook)
        notebook.add(summary_frame, text="Summary")
        
        # Detailed results tab
        detailed_frame = ttk.Frame(notebook)
        notebook.add(detailed_frame, text="Detailed Results")
        
        self.create_summary_tab(summary_frame)
        self.create_detailed_tab(detailed_frame)
        
        # Add export button
        export_frame = ttk.Frame(results_window)
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(export_frame, text="Export All Results to Excel", 
                  command=self.export_batch_results).pack(side=tk.RIGHT, padx=5)
    
    def create_summary_tab(self, parent):
        """Create summary tab for batch results"""
        # Create treeview for summary
        columns = ('Filename', 't8/5 (s)', 'Avg Cooling Rate (°C/s)', 'Avg Cooling t8/5 (°C/s)', 
                  'Lowest Cooling t8/5 (°C/s)', 'Phase Change Time (s)')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=20)
        
        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Add data
        for filename, data in self.batch_results.items():
            results = data['results']
            t85_stats = results['t85_cooling_stats']
            
            tree.insert('', tk.END, values=(
                filename,
                f"{results['t85']:.2f}" if not np.isnan(results['t85']) else "N/A",
                f"{results['average_cooling_rate']:.2f}" if not np.isnan(results['average_cooling_rate']) else "N/A",
                f"{t85_stats['avg_cooling_rate_t85']:.2f}" if not np.isnan(t85_stats['avg_cooling_rate_t85']) else "N/A",
                f"{t85_stats['min_cooling_rate_t85']:.2f}" if not np.isnan(t85_stats['min_cooling_rate_t85']) else "N/A",
                f"{results['phase_change_time']:.2f}" if not np.isnan(results['phase_change_time']) else "N/A"
            ))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_detailed_tab(self, parent):
        """Create detailed results tab"""
        # Create text widget for detailed results
        text_widget = tk.Text(parent, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Populate with detailed results
        for filename, data in self.batch_results.items():
            results = data['results']
            t85_stats = results['t85_cooling_stats']
            
            text_widget.insert(tk.END, f"=== {filename} ===\n")
            text_widget.insert(tk.END, f"t8/5 Time: {results['t85']:.2f} seconds\n")
            text_widget.insert(tk.END, f"Average Cooling Rate (Overall): {results['average_cooling_rate']:.2f} °C/s\n")
            
            if not np.isnan(t85_stats['avg_cooling_rate_t85']):
                text_widget.insert(tk.END, f"Average Cooling Rate (800-500°C): {t85_stats['avg_cooling_rate_t85']:.2f} °C/s\n")
                text_widget.insert(tk.END, f"Lowest Cooling Rate (800-500°C): {t85_stats['min_cooling_rate_t85']:.2f} °C/s\n")
                text_widget.insert(tk.END, f"Time at Lowest Cooling Rate: {t85_stats['time_at_min_cooling_t85']:.2f} seconds\n")
            else:
                text_widget.insert(tk.END, "Cooling rate analysis within t8/5 range: Not available\n")
            
            text_widget.insert(tk.END, f"Phase Change Time: {results['phase_change_time']:.2f} seconds\n")
            text_widget.insert(tk.END, f"Max Temperature: {results['max_temperature']:.1f} °C\n")
            text_widget.insert(tk.END, f"Min Temperature: {results['min_temperature']:.1f} °C\n")
            text_widget.insert(tk.END, f"Cooling Rate - Max: {results['cooling_rate_max']:.2f}, Min: {results['cooling_rate_min']:.2f}, Std: {results['cooling_rate_std']:.2f}\n")
            text_widget.insert(tk.END, f"Data Points: {results['data_points']}\n")
            text_widget.insert(tk.END, "-" * 50 + "\n\n")
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def export_batch_results(self):
        """Export all batch results to Excel"""
        if not self.batch_results:
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Batch Results",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Create summary sheet
                    summary_data = []
                    for file_name, data in self.batch_results.items():
                        results = data['results']
                        t85_stats = results['t85_cooling_stats']
                        
                        summary_data.append({
                            'Filename': file_name,
                            't85_seconds': results['t85'],
                            'average_cooling_rate_C_per_s': results['average_cooling_rate'],
                            'avg_cooling_rate_t85_C_per_s': t85_stats['avg_cooling_rate_t85'],
                            'min_cooling_rate_t85_C_per_s': t85_stats['min_cooling_rate_t85'],
                            'time_at_min_cooling_t85_seconds': t85_stats['time_at_min_cooling_t85'],
                            'phase_change_time_seconds': results['phase_change_time'],
                            'max_temperature_C': results['max_temperature'],
                            'min_temperature_C': results['min_temperature'],
                            'cooling_rate_max': results['cooling_rate_max'],
                            'cooling_rate_min': results['cooling_rate_min'],
                            'cooling_rate_std': results['cooling_rate_std'],
                            'data_points': results['data_points']
                        })
                    
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Batch_Summary', index=False)
                    
                    # Create individual sheets for each file
                    for file_name, data in self.batch_results.items():
                        results = data['results']
                        
                        # Detailed data
                        detailed_df = pd.DataFrame({
                            'time': results['time_data'],
                            'temperature_original': results['temp_original'],
                            'temperature_smoothed': results['temp_smooth'],
                            'cooling_rate': results['cooling_rate_data']
                        })
                        
                        # Truncate sheet name if too long
                        sheet_name = file_name[:31] if len(file_name) > 31 else file_name
                        detailed_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                messagebox.showinfo("Success", f"Batch results exported to:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export batch results: {str(e)}")
    
    def load_file(self, filename):
        """Load the selected Excel file with better error handling"""
        try:
            # Try reading with different parameters
            self.df = pd.read_excel(filename)
            
            # Show basic info
            self.display_info(f"File loaded: {filename}")
            self.display_info(f"Shape: {self.df.shape}")
            self.display_info(f"Columns: {list(self.df.columns)}")
            
            # Update combo boxes
            columns = list(self.df.columns)
            self.time_combo['values'] = columns
            self.temp_combo['values'] = columns
            
            if len(columns) >= 2:
                self.time_combo.set(columns[0])
                self.temp_combo.set(columns[1])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def display_info(self, message):
        """Display message in info text box"""
        self.info_text.insert(tk.END, message + "\n")
        self.info_text.see(tk.END)
    
    def display_results(self, message):
        """Display message in results text box"""
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
    
    def inspect_data(self):
        """Inspect the loaded data thoroughly"""
        if self.df is None:
            messagebox.showerror("Error", "Please load a file first!")
            return
        
        self.display_info("\n" + "="*50)
        self.display_info("DATA INSPECTION")
        self.display_info("="*50)
        
        # Basic info
        self.display_info(f"DataFrame shape: {self.df.shape}")
        
        # Check for selected columns
        time_col = self.time_combo.get()
        temp_col = self.temp_combo.get()
        
        if time_col and temp_col:
            self.display_info(f"\nSelected TIME column ('{time_col}'):")
            self.display_info(f"  Dtype: {self.df[time_col].dtype}")
            self.display_info(f"  Range: {self.df[time_col].min():.4f} to {self.df[time_col].max():.4f}")
            self.display_info(f"  First 5 values: {self.df[time_col].head().tolist()}")
            self.display_info(f"  Any zeros?: {(self.df[time_col] == 0).sum()} zeros")
            self.display_info(f"  Any negative?: {(self.df[time_col] < 0).sum()} negative")
            self.display_info(f"  Any NaN?: {self.df[time_col].isna().sum()} NaN")
            
            self.display_info(f"\nSelected TEMPERATURE column ('{temp_col}'):")
            self.display_info(f"  Dtype: {self.df[temp_col].dtype}")
            self.display_info(f"  Range: {self.df[temp_col].min():.2f} to {self.df[temp_col].max():.2f} °C")
            self.display_info(f"  First 5 values: {self.df[temp_col].head().tolist()}")
            self.display_info(f"  Reaches 800°C?: {any(self.df[temp_col] >= 800)}")
            self.display_info(f"  Reaches 500°C?: {any(self.df[temp_col] >= 500)}")
            self.display_info(f"  Any NaN?: {self.df[temp_col].isna().sum()} NaN")
    
    def debug_data(self):
        """Run detailed debugging on the data"""
        if self.df is None:
            messagebox.showerror("Error", "Please load a file first!")
            return
        
        time_col = self.time_combo.get()
        temp_col = self.temp_combo.get()
        
        if not time_col or not temp_col:
            messagebox.showerror("Error", "Please select both time and temperature columns!")
            return
        
        self.display_info("\n" + "="*50)
        self.display_info("DEBUG ANALYSIS")
        self.display_info("="*50)
        
        # Check time data issues
        time_data = self.df[time_col].copy()
        temp_data = self.df[temp_col].copy()
        
        # Clean data - remove NaN and infinite values
        time_data = time_data.replace([np.inf, -np.inf], np.nan).dropna()
        temp_data = temp_data.replace([np.inf, -np.inf], np.nan).dropna()
        
        # Check for very small time increments (causing infinite cooling rates)
        time_diff = np.diff(time_data)
        self.display_info(f"Time differences - Min: {np.min(time_diff):.6f}, Max: {np.max(time_diff):.6f}")
        self.display_info(f"Zero time differences: {np.sum(time_diff == 0)}")
        
        if np.any(time_diff <= 0):
            self.display_info("❌ PROBLEM: Non-increasing time values detected!")
        
        # Check temperature range for t8/5
        temp_range = f"{temp_data.min():.1f}°C to {temp_data.max():.1f}°C"
        self.display_info(f"Temperature range: {temp_range}")
        
        if temp_data.max() < 800:
            self.display_info("❌ PROBLEM: Maximum temperature is below 800°C - cannot calculate t8/5!")
        elif temp_data.min() > 500:
            self.display_info("❌ PROBLEM: Minimum temperature is above 500°C - cannot calculate t8/5!")
        else:
            self.display_info("✅ Temperature range suitable for t8/5 calculation")
        
        # Test cooling rate calculation
        try:
            cooling_rate = np.gradient(temp_data, time_data)
            infinite_cooling = np.isinf(cooling_rate).sum()
            nan_cooling = np.isnan(cooling_rate).sum()
            
            self.display_info(f"Cooling rate stats - Infinite: {infinite_cooling}, NaN: {nan_cooling}")
            
            if infinite_cooling > 0:
                self.display_info("❌ PROBLEM: Infinite cooling rates detected! Check time data.")
            if nan_cooling > 0:
                self.display_info("❌ PROBLEM: NaN cooling rates detected! Check for missing data.")
            
            if infinite_cooling == 0 and nan_cooling == 0:
                self.display_info("✅ Cooling rate calculation successful")
                
        except Exception as e:
            self.display_info(f"❌ ERROR in cooling rate calculation: {str(e)}")
    
    def run_analysis(self):
        """Perform the Jominy analysis with robust error handling"""
        if self.df is None:
            messagebox.showerror("Error", "Please select an Excel file first!")
            return
        
        try:
            time_col = self.time_combo.get()
            temp_col = self.temp_combo.get()
            
            if not time_col or not temp_col:
                messagebox.showerror("Error", "Please select both time and temperature columns!")
                return
            
            # Clear previous results
            self.results_text.delete(1.0, tk.END)
            
            # Get analysis parameters
            window_length = int(self.window_entry.get())
            polyorder = int(self.poly_entry.get())
            cooling_threshold = float(self.threshold_entry.get())
            
            # Perform analysis
            analyzer = JominyAnalyzer(self.df, time_col, temp_col)
            self.results = analyzer.analyze_all_curves(window_length, polyorder, cooling_threshold)
            
            # Display results
            self.display_final_results()
            
            messagebox.showinfo("Success", "Analysis completed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            self.display_results(f"ERROR: {str(e)}")
    
    def display_final_results(self):
        """Display final analysis results"""
        t85_stats = self.results['t85_cooling_stats']
        
        results_text = f"""=== JOMINY TEST ANALYSIS RESULTS ===
Software Version: {self.VERSION}

t8/5 Time: {self.results['t85']:.2f} seconds
Average Cooling Rate (Overall): {self.results['average_cooling_rate']:.2f} °C/s
Phase Change Time: {self.results['phase_change_time']:.2f} seconds
Maximum Temperature: {self.results['max_temperature']:.1f} °C
Minimum Temperature: {self.results['min_temperature']:.1f} °C
Temperature Range: {self.results['max_temperature'] - self.results['min_temperature']:.1f} °C

COOLING RATE ANALYSIS WITHIN t8/5 RANGE (800-500°C):
"""
        if not np.isnan(t85_stats['avg_cooling_rate_t85']):
            results_text += f"  - Average Cooling Rate: {t85_stats['avg_cooling_rate_t85']:.2f} °C/s\n"
            results_text += f"  - Lowest Cooling Rate: {t85_stats['min_cooling_rate_t85']:.2f} °C/s\n"
            results_text += f"  - Time at Lowest Cooling Rate: {t85_stats['time_at_min_cooling_t85']:.2f} seconds\n"
        else:
            results_text += "  - Cooling rate analysis within t8/5 range: Not available\n"

        results_text += f"""
COOLING RATE STATISTICS (OVERALL):
  - Maximum: {self.results['cooling_rate_max']:.2f} °C/s
  - Minimum: {self.results['cooling_rate_min']:.2f} °C/s
  - Standard Deviation: {self.results['cooling_rate_std']:.2f} °C/s

DATA QUALITY CHECK:
  - Infinite values in cooling rate: {self.results['infinite_cooling_count']}
  - NaN values in cooling rate: {self.results['nan_cooling_count']}
  - Data points used: {self.results['data_points']}
"""
        self.display_results(results_text)
        
        # Add warnings if needed
        if self.results['infinite_cooling_count'] > 0:
            self.display_results("\n⚠️ WARNING: Infinite cooling rates detected! Check time data.")
        if self.results['nan_cooling_count'] > 0:
            self.display_results("⚠️ WARNING: NaN values in cooling rates! Check for missing data.")
        if np.isnan(self.results['t85']):
            self.display_results("⚠️ WARNING: t8/5 could not be calculated. Check temperature range (800°C-500°C).")
    
    def plot_results(self):
        """Plot the results in separate windows"""
        if not self.results:
            messagebox.showerror("Error", "Please run analysis first!")
            return
        
        try:
            # Clear previous figures
            self.figures.clear()
            
            # Create separate figures for each plot
            self.create_temperature_plot()
            self.create_cooling_rate_plot()
            self.create_combined_plot()
            
            messagebox.showinfo("Success", "Interactive charts generated in separate windows!\n\nYou can now:\n• Zoom in/out\n• Pan around\n• Reset views\n• Save individual charts")
            
        except Exception as e:
            messagebox.showerror("Error", f"Plotting failed: {str(e)}")
    
    def create_temperature_plot(self):
        """Create temperature vs time plot in separate window"""
        fig = Figure(figsize=(12, 7))
        ax = fig.add_subplot(111)
        
        time_data = self.results['time_data']
        temp_original = self.results['temp_original']
        temp_smooth = self.results['temp_smooth']
        
        ax.plot(time_data, temp_original, 'b-', alpha=0.3, label='Original', linewidth=1)
        ax.plot(time_data, temp_smooth, 'r-', linewidth=2, label='Smoothed (S-G)')
        
        # Mark t8/5 region if available
        if not np.isnan(self.results['t85']):
            ax.axhline(y=800, color='green', linestyle='--', alpha=0.7, label='800°C')
            ax.axhline(y=500, color='orange', linestyle='--', alpha=0.7, label='500°C')
            ax.set_title(f'Temperature vs Time (t8/5 = {self.results["t85"]:.2f}s)', fontsize=14, fontweight='bold')
        else:
            ax.set_title('Temperature vs Time', fontsize=14, fontweight='bold')
        
        ax.set_xlabel('Time (s)', fontsize=12)
        ax.set_ylabel('Temperature (°C)', fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='both', which='major', labelsize=10)
        
        # Create new window for this plot
        self.create_interactive_plot_window(fig, "Temperature Analysis")
        self.figures['temperature'] = fig
    
    def create_cooling_rate_plot(self):
        """Create cooling rate plot in separate window"""
        fig = Figure(figsize=(12, 7))
        ax = fig.add_subplot(111)
        
        time_data = self.results['time_data']
        cooling_rate = self.results['cooling_rate_data']
        
        ax.plot(time_data, cooling_rate, 'g-', linewidth=2, label='Cooling Rate')
        ax.set_xlabel('Time (s)', fontsize=12)
        ax.set_ylabel('Cooling Rate (°C/s)', fontsize=12)
        ax.set_title('Cooling Rate vs Time', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='both', which='major', labelsize=10)
        
        # Mark phase change region
        if not np.isnan(self.results['phase_change_time']):
            ax.axvline(x=self.results['phase_change_time'], color='red', 
                       linestyle='--', linewidth=2, label=f'Phase change: {self.results["phase_change_time"]:.2f}s')
            ax.legend(fontsize=10)
        
        # Create new window for this plot
        self.create_interactive_plot_window(fig, "Cooling Rate Analysis")
        self.figures['cooling_rate'] = fig
    
    def create_combined_plot(self):
        """Create combined plot in separate window"""
        fig = Figure(figsize=(12, 10))
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)
        
        time_data = self.results['time_data']
        temp_original = self.results['temp_original']
        temp_smooth = self.results['temp_smooth']
        cooling_rate = self.results['cooling_rate_data']
        
        # Top subplot: Temperature
        ax1.plot(time_data, temp_original, 'b-', alpha=0.3, label='Original', linewidth=1)
        ax1.plot(time_data, temp_smooth, 'r-', linewidth=2, label='Smoothed (S-G)')
        
        if not np.isnan(self.results['t85']):
            ax1.axhline(y=800, color='green', linestyle='--', alpha=0.7, label='800°C')
            ax1.axhline(y=500, color='orange', linestyle='--', alpha=0.7, label='500°C')
            ax1.set_title(f'Temperature vs Time (t8/5 = {self.results["t85"]:.2f}s)', fontsize=12, fontweight='bold')
        else:
            ax1.set_title('Temperature vs Time', fontsize=12, fontweight='bold')
        
        ax1.set_ylabel('Temperature (°C)', fontsize=11)
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='both', which='major', labelsize=9)
        
        # Bottom subplot: Cooling Rate
        ax2.plot(time_data, cooling_rate, 'g-', linewidth=2, label='Cooling Rate')
        ax2.set_xlabel('Time (s)', fontsize=11)
        ax2.set_ylabel('Cooling Rate (°C/s)', fontsize=11)
        ax2.set_title('Cooling Rate vs Time', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='both', which='major', labelsize=9)
        
        if not np.isnan(self.results['phase_change_time']):
            ax2.axvline(x=self.results['phase_change_time'], color='red', 
                       linestyle='--', linewidth=2, label=f'Phase change: {self.results["phase_change_time"]:.2f}s')
            ax2.legend(fontsize=9)
        
        fig.tight_layout()
        
        # Create new window for this plot
        self.create_interactive_plot_window(fig, "Combined Analysis")
        self.figures['combined'] = fig
    
    def create_interactive_plot_window(self, fig, title):
        """Create a new window for an interactive matplotlib figure"""
        plot_window = tk.Toplevel(self.root)
        plot_window.title(f"{title} - Interactive")
        plot_window.geometry("1000x700")
        
        # Create canvas with navigation toolbar
        canvas = FigureCanvasTkAgg(fig, plot_window)
        canvas.draw()
        
        # Create toolbar for interactive features
        toolbar = NavigationToolbar2Tk(canvas, plot_window)
        toolbar.update()
        
        # Pack canvas and toolbar
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add save button to plot window
        save_frame = ttk.Frame(plot_window)
        save_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(save_frame, text="Save This Chart as PNG", 
                  command=lambda: self.save_single_chart(fig, title)).pack(side=tk.RIGHT, padx=5)
        
        # Add info label about interactive features
        info_label = ttk.Label(save_frame, 
                              text="Use toolbar above to: Zoom • Pan • Reset • Save",
                              font=('Arial', 9))
        info_label.pack(side=tk.LEFT, padx=5)
    
    def save_charts(self):
        """Save all charts to PNG files"""
        if not self.figures:
            messagebox.showerror("Error", "Please generate charts first using 'Plot Results'!")
            return
        
        # Ask for directory to save charts
        directory = filedialog.askdirectory(title="Select directory to save charts")
        if not directory:
            return
        
        try:
            saved_files = []
            for name, fig in self.figures.items():
                # Save as PNG only
                png_path = os.path.join(directory, f"jominy_{name}.png")
                fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
                saved_files.append(png_path)
            
            if saved_files:
                file_list = "\n".join([os.path.basename(f) for f in saved_files])
                messagebox.showinfo("Success", 
                                  f"Charts saved successfully as PNG!\n\nSaved files:\n{file_list}")
            else:
                messagebox.showerror("Error", "No charts could be saved!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save charts: {str(e)}")
    
    def save_single_chart(self, fig, title):
        """Save a single chart to PNG file"""
        if not fig:
            return
        
        # Ask for filename
        filename = filedialog.asksaveasfilename(
            title=f"Save {title} as PNG",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
                messagebox.showinfo("Success", f"Chart saved to:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save chart: {str(e)}")
    
    def save_results(self):
        """Save results to Excel file"""
        if not self.results:
            messagebox.showerror("Error", "Please run analysis first!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Results As",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                analyzer = JominyAnalyzer(self.df, self.time_combo.get(), self.temp_combo.get())
                analyzer.save_to_excel(filename, self.results)
                messagebox.showinfo("Success", f"Results saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

# [The JominyAnalyzer class remains exactly the same as in v6.0]
class JominyAnalyzer:
    def __init__(self, df, time_col, temp_col):
        self.df = df
        self.time_col = time_col
        self.temp_col = temp_col
    
    def clean_data(self, time_data, temp_data):
        """Clean data by removing NaN and infinite values"""
        # Create a mask for valid data points
        mask = (~np.isnan(time_data)) & (~np.isnan(temp_data)) & (~np.isinf(time_data)) & (~np.isinf(temp_data))
        return time_data[mask], temp_data[mask]
    
    def smooth_curves(self, time_data, temp_data, window_length=11, polyorder=3):
        """Apply Savitzky-Golay filter for smoothing with validation"""
        # Ensure window length is appropriate
        n_points = len(temp_data)
        if window_length > n_points:
            window_length = n_points - 1 if n_points % 2 == 0 else n_points
            if window_length < polyorder:
                window_length = polyorder + 2
        
        # Ensure window length is odd
        if window_length % 2 == 0:
            window_length += 1
        
        try:
            return savgol_filter(temp_data, window_length, polyorder)
        except:
            # Fallback: use moving average if S-G fails
            return pd.Series(temp_data).rolling(window=5, center=True).mean().fillna(temp_data)
    
    def calculate_cooling_rate(self, time_data, temp_data):
        """Calculate cooling rate (dT/dt) with error handling"""
        try:
            dt = np.gradient(time_data)
            dT = np.gradient(temp_data)
            cooling_rate = dT / dt
            
            # Replace infinite values with NaN
            cooling_rate = np.where(np.isinf(cooling_rate), np.nan, cooling_rate)
            
            return cooling_rate
        except:
            return np.full_like(time_data, np.nan)
    
    def find_t85(self, time_data, temp_data):
        """Calculate t8/5 - time between 800°C and 500°C"""
        try:
            # Check if we have data in the required range
            if (temp_data.max() < 800) or (temp_data.min() > 500):
                return np.nan
            
            # Create interpolation function
            valid_mask = ~np.isnan(temp_data)
            if np.sum(valid_mask) < 2:
                return np.nan
                
            f = interp1d(temp_data[valid_mask], time_data[valid_mask], 
                         bounds_error=False, fill_value=np.nan)
            
            t_800 = f(800)
            t_500 = f(500)
            
            if np.isnan(t_800) or np.isnan(t_500):
                return np.nan
            
            t85 = abs(t_500 - t_800)
            return t85
        except:
            return np.nan
    
    def calculate_cooling_stats_t85(self, time_data, temp_data, cooling_rate):
        """Calculate cooling rate statistics within t8/5 range"""
        try:
            # Check if we have data in the required range
            if (temp_data.max() < 800) or (temp_data.min() > 500):
                return {
                    'avg_cooling_rate_t85': np.nan,
                    'min_cooling_rate_t85': np.nan,
                    'time_at_min_cooling_t85': np.nan
                }
            
            # Create interpolation function for temperature to time
            valid_mask = ~np.isnan(temp_data)
            if np.sum(valid_mask) < 2:
                return {
                    'avg_cooling_rate_t85': np.nan,
                    'min_cooling_rate_t85': np.nan,
                    'time_at_min_cooling_t85': np.nan
                }
                
            f_temp_to_time = interp1d(temp_data[valid_mask], time_data[valid_mask], 
                                     bounds_error=False, fill_value=np.nan)
            
            # Get time points for 800°C and 500°C
            t_800 = f_temp_to_time(800)
            t_500 = f_temp_to_time(500)
            
            if np.isnan(t_800) or np.isnan(t_500):
                return {
                    'avg_cooling_rate_t85': np.nan,
                    'min_cooling_rate_t85': np.nan,
                    'time_at_min_cooling_t85': np.nan
                }
            
            # Ensure correct order (time should be increasing)
            t_start = min(t_800, t_500)
            t_end = max(t_800, t_500)
            
            # Find data points within t8/5 range
            mask_t85 = (time_data >= t_start) & (time_data <= t_end)
            cooling_rate_t85 = cooling_rate[mask_t85]
            time_t85 = time_data[mask_t85]
            
            if len(cooling_rate_t85) == 0:
                return {
                    'avg_cooling_rate_t85': np.nan,
                    'min_cooling_rate_t85': np.nan,
                    'time_at_min_cooling_t85': np.nan
                }
            
            # Remove NaN values from cooling rate within t8/5 range
            valid_cooling_mask = ~np.isnan(cooling_rate_t85)
            if np.sum(valid_cooling_mask) == 0:
                return {
                    'avg_cooling_rate_t85': np.nan,
                    'min_cooling_rate_t85': np.nan,
                    'time_at_min_cooling_t85': np.nan
                }
            
            valid_cooling_t85 = cooling_rate_t85[valid_cooling_mask]
            valid_time_t85 = time_t85[valid_cooling_mask]
            
            # Calculate statistics
            avg_cooling_t85 = np.mean(valid_cooling_t85)
            min_cooling_t85 = np.min(valid_cooling_t85)
            min_cooling_idx = np.argmin(valid_cooling_t85)
            time_at_min_cooling = valid_time_t85.iloc[min_cooling_idx]
            
            return {
                'avg_cooling_rate_t85': avg_cooling_t85,
                'min_cooling_rate_t85': min_cooling_t85,
                'time_at_min_cooling_t85': time_at_min_cooling
            }
            
        except:
            return {
                'avg_cooling_rate_t85': np.nan,
                'min_cooling_rate_t85': np.nan,
                'time_at_min_cooling_t85': np.nan
            }
    
    def find_phase_change(self, time_data, cooling_rate, threshold=1.0):
        """Find time when cooling rate approaches zero (phase change)"""
        try:
            # Find regions where cooling rate is near zero
            valid_cooling = cooling_rate[~np.isnan(cooling_rate)]
            valid_times = time_data[~np.isnan(cooling_rate)]
            
            if len(valid_cooling) == 0:
                return np.nan
            
            near_zero = np.where(np.abs(valid_cooling) < threshold)[0]
            
            if len(near_zero) > 0:
                # Return the first significant near-zero point
                return valid_times.iloc[near_zero[0]]
            else:
                return np.nan
        except:
            return np.nan
    
    def analyze_all_curves(self, window_length=11, polyorder=3, cooling_threshold=1.0):
        """Main analysis function with comprehensive error handling"""
        # Clean data first
        time_data, temp_data = self.clean_data(
            self.df[self.time_col].copy(), 
            self.df[self.temp_col].copy()
        )
        
        # Smooth data
        temp_smooth = self.smooth_curves(time_data, temp_data, window_length, polyorder)
        
        # Calculate cooling rate
        cooling_rate = self.calculate_cooling_rate(time_data, temp_smooth)
        
        # Find key parameters
        t85 = self.find_t85(time_data, temp_smooth)
        phase_change_time = self.find_phase_change(time_data, cooling_rate, cooling_threshold)
        
        # Calculate cooling rate statistics within t8/5 range
        t85_cooling_stats = self.calculate_cooling_stats_t85(time_data, temp_smooth, cooling_rate)
        
        # Count data issues
        infinite_cooling_count = np.sum(np.isinf(cooling_rate))
        nan_cooling_count = np.sum(np.isnan(cooling_rate))
        
        # Calculate cooling rate statistics on valid data only
        valid_cooling = cooling_rate[~np.isnan(cooling_rate) & ~np.isinf(cooling_rate)]
        
        if len(valid_cooling) > 0:
            avg_cooling = np.mean(valid_cooling)
            max_cooling = np.max(valid_cooling)
            min_cooling = np.min(valid_cooling)
            std_cooling = np.std(valid_cooling)
        else:
            avg_cooling = max_cooling = min_cooling = std_cooling = np.nan
        
        # Compile results
        results = {
            't85': t85,
            'average_cooling_rate': avg_cooling,
            'phase_change_time': phase_change_time,
            'max_temperature': np.max(temp_smooth),
            'min_temperature': np.min(temp_smooth),
            'cooling_rate_max': max_cooling,
            'cooling_rate_min': min_cooling,
            'cooling_rate_std': std_cooling,
            'infinite_cooling_count': infinite_cooling_count,
            'nan_cooling_count': nan_cooling_count,
            'data_points': len(time_data),
            'time_data': time_data,
            'temp_original': temp_data,
            'temp_smooth': temp_smooth,
            'cooling_rate_data': cooling_rate,
            't85_cooling_stats': t85_cooling_stats
        }
        
        return results
    
    def save_to_excel(self, filename, results):
        """Save results to Excel file"""
        # Create results dataframe
        t85_stats = results['t85_cooling_stats']
        
        results_df = pd.DataFrame([{
            't85_seconds': results['t85'],
            'average_cooling_rate_C_per_s': results['average_cooling_rate'],
            'avg_cooling_rate_t85_C_per_s': t85_stats['avg_cooling_rate_t85'],
            'min_cooling_rate_t85_C_per_s': t85_stats['min_cooling_rate_t85'],
            'time_at_min_cooling_t85_seconds': t85_stats['time_at_min_cooling_t85'],
            'phase_change_time_seconds': results['phase_change_time'],
            'max_temperature_C': results['max_temperature'],
            'min_temperature_C': results['min_temperature'],
            'cooling_rate_max': results['cooling_rate_max'],
            'cooling_rate_min': results['cooling_rate_min'],
            'cooling_rate_std': results['cooling_rate_std'],
            'infinite_values_count': results['infinite_cooling_count'],
            'nan_values_count': results['nan_cooling_count'],
            'data_points_used': results['data_points']
        }])
        
        # Create detailed data with calculations
        detailed_df = pd.DataFrame({
            'time': results['time_data'],
            'temperature_original': results['temp_original'],
            'temperature_smoothed': results['temp_smooth'],
            'cooling_rate': results['cooling_rate_data']
        })
        
        # Write to Excel with multiple sheets
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            detailed_df.to_excel(writer, sheet_name='Detailed_Data', index=False)
            results_df.to_excel(writer, sheet_name='Analysis_Results', index=False)
            
            # Add summary statistics
            summary = pd.DataFrame({
                'Parameter': [
                    't8/5 (s)', 'Average Cooling Rate (°C/s)', 
                    'Avg Cooling Rate t8/5 (°C/s)', 'Lowest Cooling Rate t8/5 (°C/s)',
                    'Phase Change Time (s)', 'Max Temperature (°C)', 
                    'Min Temperature (°C)', 'Temperature Range (°C)',
                    'Data Points Used', 'Data Quality Issues'
                ],
                'Value': [
                    results['t85'], results['average_cooling_rate'],
                    t85_stats['avg_cooling_rate_t85'], t85_stats['min_cooling_rate_t85'],
                    results['phase_change_time'], results['max_temperature'],
                    results['min_temperature'], 
                    results['max_temperature'] - results['min_temperature'],
                    results['data_points'],
                    f"{results['infinite_cooling_count']} infinite, {results['nan_cooling_count']} NaN"
                ]
            })
            summary.to_excel(writer, sheet_name='Summary', index=False)

def main():
    root = tk.Tk()
    app = JominyDebugAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
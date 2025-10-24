import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Rectangle
import matplotlib.gridspec as gridspec
from matplotlib.cm import ScalarMappable

class HeatTransferSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Heat Transfer Simulator v8.2 - Physics Corrected")
        self.root.geometry("1300x700")
        self.root.minsize(1200, 600)
        
        # Create main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for controls
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        control_frame.pack_propagate(False)
        
        # Right panel for plots and info tabs
        self.right_frame = ttk.Frame(main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Plots
        self.plot_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.plot_frame, text="Simulation Results")
        
        # Tab 2: Developer Info
        self.dev_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dev_frame, text="Developer Info")
        
        # Tab 3: License
        self.license_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.license_frame, text="MIT License")
        
        # Tab 4: Disclaimer
        self.disclaimer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.disclaimer_frame, text="Disclaimer")
        
        # Tab 5: Changelog
        self.changelog_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.changelog_frame, text="Version Changelog")
        
        # Tab 6: References
        self.references_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.references_frame, text="References")
        
        # Input fields - Cooling Conditions
        input_frame = ttk.LabelFrame(control_frame, text="Cooling Conditions", padding=5)
        input_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Cooling parameters
        ttk.Label(input_frame, text="Waterjet h:").grid(row=0, column=0, sticky=tk.W)
        self.h_waterjet = ttk.Entry(input_frame, width=8)
        self.h_waterjet.insert(0, "5000")
        self.h_waterjet.grid(row=0, column=1, padx=2, pady=1)
        
        ttk.Label(input_frame, text="Natural h:").grid(row=1, column=0, sticky=tk.W)
        self.h_natural = ttk.Entry(input_frame, width=8)
        self.h_natural.insert(0, "10")
        self.h_natural.grid(row=1, column=1, padx=2, pady=1)
        
        ttk.Label(input_frame, text="Coolant °C:").grid(row=2, column=0, sticky=tk.W)
        self.T_coolant = ttk.Entry(input_frame, width=8)
        self.T_coolant.insert(0, "20")
        self.T_coolant.grid(row=2, column=1, padx=2, pady=1)
        
        ttk.Label(input_frame, text="Initial °C:").grid(row=3, column=0, sticky=tk.W)
        self.T_init = ttk.Entry(input_frame, width=8)
        self.T_init.insert(0, "900")
        self.T_init.grid(row=3, column=1, padx=2, pady=1)
        
        ttk.Label(input_frame, text="Time (s):").grid(row=4, column=0, sticky=tk.W)
        self.sim_time = ttk.Entry(input_frame, width=8)
        self.sim_time.insert(0, "15")
        self.sim_time.grid(row=4, column=1, padx=2, pady=1)
        
        # Geometry Configuration
        geom_frame = ttk.LabelFrame(control_frame, text="Specimen Geometry (mm)", padding=5)
        geom_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Square Bar Geometry
        ttk.Label(geom_frame, text="Square:", font='Arial 8 bold').grid(row=0, column=0, sticky=tk.W, pady=(0,2))
        ttk.Label(geom_frame, text="W:").grid(row=1, column=0, sticky=tk.W)
        self.square_width = ttk.Entry(geom_frame, width=6)
        self.square_width.insert(0, "6.0")
        self.square_width.grid(row=1, column=1, padx=2, pady=1)
        ttk.Label(geom_frame, text="H:").grid(row=1, column=2, sticky=tk.W)
        self.square_height = ttk.Entry(geom_frame, width=6)
        self.square_height.insert(0, "75.0")
        self.square_height.grid(row=1, column=3, padx=2, pady=1)
        
        # Cylindrical Bar Geometry
        ttk.Label(geom_frame, text="Cylinder:", font='Arial 8 bold').grid(row=2, column=0, sticky=tk.W, pady=(5,2))
        ttk.Label(geom_frame, text="D:").grid(row=3, column=0, sticky=tk.W)
        self.cyl_diameter = ttk.Entry(geom_frame, width=6)
        self.cyl_diameter.insert(0, "19.05")
        self.cyl_diameter.grid(row=3, column=1, padx=2, pady=1)
        ttk.Label(geom_frame, text="H:").grid(row=3, column=2, sticky=tk.W)
        self.cyl_height = ttk.Entry(geom_frame, width=6)
        self.cyl_height.insert(0, "75.0")
        self.cyl_height.grid(row=3, column=3, padx=2, pady=1)
        
        # Conical Tip Bar Geometry
        ttk.Label(geom_frame, text="Conical:", font='Arial 8 bold').grid(row=4, column=0, sticky=tk.W, pady=(5,2))
        ttk.Label(geom_frame, text="D:").grid(row=5, column=0, sticky=tk.W)
        self.cone_cyl_diameter = ttk.Entry(geom_frame, width=6)
        self.cone_cyl_diameter.insert(0, "19.05")
        self.cone_cyl_diameter.grid(row=5, column=1, padx=2, pady=1)
        ttk.Label(geom_frame, text="Cyl H:").grid(row=5, column=2, sticky=tk.W)
        self.cone_cyl_height = ttk.Entry(geom_frame, width=6)
        self.cone_cyl_height.insert(0, "65.0")
        self.cone_cyl_height.grid(row=5, column=3, padx=2, pady=1)
        ttk.Label(geom_frame, text="Cone H:").grid(row=6, column=0, sticky=tk.W)
        self.cone_tip_height = ttk.Entry(geom_frame, width=6)
        self.cone_tip_height.insert(0, "10.0")
        self.cone_tip_height.grid(row=6, column=1, padx=2, pady=1)
        ttk.Label(geom_frame, text="°:").grid(row=6, column=2, sticky=tk.W)
        self.cone_angle = ttk.Entry(geom_frame, width=6)
        self.cone_angle.insert(0, "30.0")
        self.cone_angle.grid(row=6, column=3, padx=2, pady=1)
        
        # Material selection
        mat_frame = ttk.LabelFrame(control_frame, text="Material Properties", padding=5)
        mat_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(mat_frame, text="Material:").grid(row=0, column=0, sticky=tk.W)
        self.material_var = tk.StringVar(value="Steel")
        material_combo = ttk.Combobox(mat_frame, textvariable=self.material_var, 
                                    values=["Steel", "Copper", "Aluminum", "Custom"], width=8)
        material_combo.grid(row=0, column=1, padx=2, pady=1)
        material_combo.bind('<<ComboboxSelected>>', self.update_material_properties)
        
        ttk.Label(mat_frame, text="k:").grid(row=1, column=0, sticky=tk.W)
        self.k = ttk.Entry(mat_frame, width=8)
        self.k.insert(0, "50")
        self.k.grid(row=1, column=1, padx=2, pady=1)
        ttk.Label(mat_frame, text="ρ:").grid(row=2, column=0, sticky=tk.W)
        self.rho = ttk.Entry(mat_frame, width=8)
        self.rho.insert(0, "7800")
        self.rho.grid(row=2, column=1, padx=2, pady=1)
        ttk.Label(mat_frame, text="Cp:").grid(row=3, column=0, sticky=tk.W)
        self.cp = ttk.Entry(mat_frame, width=8)
        self.cp.insert(0, "500")
        self.cp.grid(row=3, column=1, padx=2, pady=1)
        
        # Resolution selection
        res_frame = ttk.LabelFrame(control_frame, text="Resolution", padding=5)
        res_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.resolution_var = tk.StringVar(value="Low")
        ttk.Radiobutton(res_frame, text="Low (Fastest)", variable=self.resolution_var, 
                       value="Low").pack(anchor=tk.W, pady=1)
        ttk.Radiobutton(res_frame, text="Medium", variable=self.resolution_var, 
                       value="Medium").pack(anchor=tk.W, pady=1)
        ttk.Radiobutton(res_frame, text="High (Slow)", variable=self.resolution_var, 
                       value="High").pack(anchor=tk.W, pady=1)
        
        # Simulation Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.run_btn = ttk.Button(button_frame, text="Start Simulation", command=self.run_simulation)
        self.run_btn.pack(fill=tk.X, pady=2)
        self.reset_btn = ttk.Button(button_frame, text="Reset Geometry", command=self.reset_geometry)
        self.reset_btn.pack(fill=tk.X, pady=2)
        
        # Information Buttons
        info_frame = ttk.LabelFrame(control_frame, text="Information Tabs", padding=5)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text="Click tabs above to view:", font='Arial 8 bold').pack(pady=2)
        ttk.Label(info_frame, text="• Developer Information", font='Arial 8').pack(anchor=tk.W, pady=1)
        ttk.Label(info_frame, text="• MIT License", font='Arial 8').pack(anchor=tk.W, pady=1)
        ttk.Label(info_frame, text="• Disclaimer", font='Arial 8').pack(anchor=tk.W, pady=1)
        ttk.Label(info_frame, text="• Version Changelog", font='Arial 8').pack(anchor=tk.W, pady=1)
        ttk.Label(info_frame, text="• References & Bibliography", font='Arial 8').pack(anchor=tk.W, pady=1)
        
        # Status
        self.status_var = tk.StringVar(value="Ready to simulate")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, 
                               foreground="blue", font='Arial 8')
        status_label.pack(pady=3)
        
        # Create custom colormap
        self.cmap = LinearSegmentedColormap.from_list('blue_red', 
                    ['darkblue', 'blue', 'cyan', 'yellow', 'red', 'darkred'])
        
        # Initialize plots and info tabs
        self.setup_plots()
        self.setup_info_tabs()
        self.setup_references_tab()
        
        # Initialize colorbar
        self.colorbar = None
    
    def setup_info_tabs(self):
        """Setup the content for all information tabs"""
        # Developer Info Tab
        dev_text = """Developer Information

Name: Luis Rodrigo Palomera (A240619)
Institution: IPN - CICATA Querétaro
CVU: 881822
SECIHTI: 4021946
GitHub: lpalomerar2400
Email: palomera.luis@gmail.com

About:
This heat transfer simulation software was developed for academic and research purposes. 
It provides advanced thermal analysis capabilities for various specimen geometries 
including square bars, cylindrical bars, and conical tip bars."""

        dev_text_widget = tk.Text(self.dev_frame, wrap=tk.WORD, font=('Arial', 10), padx=10, pady=10)
        dev_scrollbar = ttk.Scrollbar(self.dev_frame, orient=tk.VERTICAL, command=dev_text_widget.yview)
        dev_text_widget.configure(yscrollcommand=dev_scrollbar.set)
        dev_text_widget.insert(tk.END, dev_text)
        dev_text_widget.config(state=tk.DISABLED)
        dev_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dev_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # License Tab
        license_text = """MIT License

Copyright (c) 2025 Luis Rodrigo Palomera

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

        license_text_widget = tk.Text(self.license_frame, wrap=tk.WORD, font=('Courier New', 9), padx=10, pady=10)
        license_scrollbar = ttk.Scrollbar(self.license_frame, orient=tk.VERTICAL, command=license_text_widget.yview)
        license_text_widget.configure(yscrollcommand=license_scrollbar.set)
        license_text_widget.insert(tk.END, license_text)
        license_text_widget.config(state=tk.DISABLED)
        license_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        license_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Disclaimer Tab
        disclaimer_text = """Disclaimer

The content of this software is provided "as is" for informational purposes only. 

The author does not warrant the accuracy, completeness, or usefulness of the 
information contained or generated herein. Any action you take based on the 
information presented is at your own risk. 

The author will not be liable for any loss or damage, including, without 
limitation, indirect or consequential loss, or any loss or damage arising 
from loss of data or profits, arising from the use of this software.

Reproduction, distribution, or use of this text, in part or in whole, is 
permitted provided that appropriate credit is given to the original author. 

Commercial use of the content is prohibited without the express permission 
of the author. 

For further inquiries or special permissions, please contact the author at:
palomera.luis@gmail.com"""

        disclaimer_text_widget = tk.Text(self.disclaimer_frame, wrap=tk.WORD, font=('Arial', 10), padx=10, pady=10)
        disclaimer_scrollbar = ttk.Scrollbar(self.disclaimer_frame, orient=tk.VERTICAL, command=disclaimer_text_widget.yview)
        disclaimer_text_widget.configure(yscrollcommand=disclaimer_scrollbar.set)
        disclaimer_text_widget.insert(tk.END, disclaimer_text)
        disclaimer_text_widget.config(state=tk.DISABLED)
        disclaimer_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        disclaimer_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Changelog Tab
        changelog_text = """Heat Transfer Simulator - Version Changelog

Version 8.2 - Current Release
• ADDED: References tab with comprehensive bibliography
• ADDED: Colorbar scale for temperature visualization
• FIXED: Corrected cylindrical bar physics with proper 2D axisymmetric formulation
• FIXED: Proper boundary conditions for cylindrical coordinates
• FIXED: Realistic cooling rates for cylindrical specimens
• IMPROVED: Conservative time stepping for numerical stability
• IMPROVED: Centerline treatment using L'Hopital's rule at r=0

Version 7.0 - Physics Correction
• FIXED: Missing messagebox import causing crashes
• FIXED: Restored correct geometry defaults (19.05mm diameter)
• FIXED: Added missing axis labels in plots
• IMPROVED: Enhanced error handling and validation

Version 6.0 - Tabbed Interface
• Added tabbed interface for better organization
• Added Developer Info, MIT License, Disclaimer, and Changelog tabs
• Enhanced error handling with detailed exception messages
• Improved boundary condition calculations for all geometries
• Added minimum grid size validation to prevent crashes
• Optimized time step calculations for numerical stability

Version 5.0 - Stability Improvements
• Fixed division by zero errors in cylindrical coordinates
• Added comprehensive bounds checking for array indices
• Implemented safeguards for minimum grid sizes
• Enhanced numerical stability with positive time step enforcement
• Added robust error handling throughout simulation methods

Version 4.0 - Performance Optimization
• Implemented vectorized operations for faster computations
• Added resolution presets (Low, Medium, High) for speed control
• Optimized time stepping algorithms
• Reduced memory usage with efficient array operations
• Improved convergence criteria for faster simulations

Version 3.0 - Multi-Geometry Support
• Added conical tip bar simulation capability
• Implemented cylindrical coordinate system for cylindrical bars
• Enhanced boundary condition handling for different geometries
• Added geometry-specific resolution parameters
• Improved visualization for all specimen types

Version 2.0 - GUI Enhancement
• Developed comprehensive Tkinter-based GUI
• Added material property database (Steel, Copper, Aluminum, Custom)
• Implemented real-time parameter controls
• Added interactive plotting with matplotlib integration
• Included temperature history tracking and visualization

Version 1.0 - Initial Release
• Basic heat transfer simulation for square bars
• Fundamental finite difference implementation
• Simple boundary condition handling
• Basic temperature field visualization
• Core numerical solver implementation

Future Plans:
• 3D visualization capabilities
• Transient boundary condition support
• Material database expansion
• Export functionality for results
• Parallel processing for faster computations"""

        changelog_text_widget = tk.Text(self.changelog_frame, wrap=tk.WORD, font=('Courier New', 9), padx=10, pady=10)
        changelog_scrollbar = ttk.Scrollbar(self.changelog_frame, orient=tk.VERTICAL, command=changelog_text_widget.yview)
        changelog_text_widget.configure(yscrollcommand=changelog_scrollbar.set)
        changelog_text_widget.insert(tk.END, changelog_text)
        changelog_text_widget.config(state=tk.DISABLED)
        changelog_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        changelog_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_references_tab(self):
        """Setup the references and bibliography tab"""
        references_text = """Heat Transfer Simulation - References & Bibliography

Fundamental Heat Transfer Theory:

[1] Incropera, F. P., DeWitt, D. P., Bergman, T. L., & Lavine, A. S. (2007).
    Fundamentals of Heat and Mass Transfer (6th ed.). John Wiley & Sons.
    - Standard textbook for heat transfer fundamentals
    - Finite difference methods for transient conduction
    - Convective boundary conditions

[2] Çengel, Y. A., & Ghajar, A. J. (2015). 
    Heat and Mass Transfer: Fundamentals & Applications (5th ed.). McGraw-Hill.
    - Lumped system analysis
    - Transient heat conduction in various geometries
    - Numerical methods in heat transfer

Numerical Methods & Finite Differences:

[3] Patankar, S. V. (1980). 
    Numerical Heat Transfer and Fluid Flow. Hemisphere Publishing.
    - Finite volume method fundamentals
    - Treatment of boundary conditions
    - Stability criteria for explicit methods

[4] Anderson, J. D. (1995). 
    Computational Fluid Dynamics: The Basics with Applications. McGraw-Hill.
    - Finite difference discretization
    - Grid generation techniques
    - Numerical stability analysis

Materials Science & Properties:

[5] Mills, K. C. (2002). 
    Recommended Values of Thermophysical Properties for Selected Commercial Alloys.
    Woodhead Publishing.
    - Temperature-dependent properties of steels
    - Thermal conductivity data
    - Specific heat capacity measurements

[6] Touloukian, Y. S., & Ho, C. Y. (Eds.). (1970). 
    Thermophysical Properties of Matter (13 volumes). IFI/Plenum.
    - Comprehensive material property database
    - Thermal diffusivity calculations
    - Density and specific heat data

Computational Implementation:

[7] Press, W. H., Teukolsky, S. A., Vetterling, W. T., & Flannery, B. P. (2007).
    Numerical Recipes: The Art of Scientific Computing (3rd ed.). Cambridge University Press.
    - PDE solution techniques
    - Visualization methods
    - Performance optimization

[8] Langtangen, H. P. (2009). 
    Python Scripting for Computational Science (3rd ed.). Springer.
    - Scientific Python programming
    - Matplotlib visualization
    - GUI development with Tkinter

Specific Applications:

[9] Minkowycz, W. J., Sparrow, E. M., & Murthy, J. Y. (Eds.). (2006).
    Handbook of Numerical Heat Transfer (2nd ed.). John Wiley & Sons.
    - Cylindrical coordinate formulations
    - Convective boundary treatments
    - Axisymmetric problems

[10] Özişik, M. N. (1993). 
     Heat Conduction (2nd ed.). John Wiley & Sons.
     - Analytical solutions for comparison
     - Transient conduction in cylinders
     - Interface conditions

Cooling Processes & Industrial Applications:

[11] Lienhard, J. H. (2019). 
     A Heat Transfer Textbook (5th ed.). Phlogiston Press.
     - Jet impingement cooling
     - Industrial heat treatment processes
     - Non-dimensional analysis

[12] Holman, J. P. (2010). 
     Heat Transfer (10th ed.). McGraw-Hill.
     - Experimental correlation validation
     - Heat transfer coefficients
     - Practical engineering applications

Software & Programming:

[13] Hunter, J. D. (2007). 
     "Matplotlib: A 2D Graphics Environment". Computing in Science & Engineering.
     - Visualization techniques used in this software

[14] Python Software Foundation. (2023). 
     Python Language Reference. https://www.python.org
     - Core programming language

[15] Tkinter Documentation. (2023).
     https://docs.python.org/3/library/tkinter.html
     - GUI framework implementation

Open Source Libraries Used:
- NumPy: Array operations and numerical computations
- Matplotlib: Scientific visualization and plotting
- Tkinter: Graphical user interface

This software implements finite difference methods for transient heat conduction
with convective boundary conditions, following established numerical methods
from the heat transfer literature."""

        references_text_widget = tk.Text(self.references_frame, wrap=tk.WORD, font=('Arial', 9), padx=10, pady=10)
        references_scrollbar = ttk.Scrollbar(self.references_frame, orient=tk.VERTICAL, command=references_text_widget.yview)
        references_text_widget.configure(yscrollcommand=references_scrollbar.set)
        references_text_widget.insert(tk.END, references_text)
        references_text_widget.config(state=tk.DISABLED)
        references_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        references_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def reset_geometry(self):
        """Reset all geometry fields to default values"""
        self.square_width.delete(0, tk.END); self.square_width.insert(0, "6.0")
        self.square_height.delete(0, tk.END); self.square_height.insert(0, "75.0")
        self.cyl_diameter.delete(0, tk.END); self.cyl_diameter.insert(0, "19.05")
        self.cyl_height.delete(0, tk.END); self.cyl_height.insert(0, "75.0")
        self.cone_cyl_diameter.delete(0, tk.END); self.cone_cyl_diameter.insert(0, "19.05")
        self.cone_cyl_height.delete(0, tk.END); self.cone_cyl_height.insert(0, "65.0")
        self.cone_tip_height.delete(0, tk.END); self.cone_tip_height.insert(0, "10.0")
        self.cone_angle.delete(0, tk.END); self.cone_angle.insert(0, "30.0")
        
    def update_material_properties(self, event=None):
        """Update material properties based on selection"""
        material = self.material_var.get()
        if material == "Steel":
            self.k.delete(0, tk.END); self.k.insert(0, "50")
            self.rho.delete(0, tk.END); self.rho.insert(0, "7800") 
            self.cp.delete(0, tk.END); self.cp.insert(0, "500")
        elif material == "Copper":
            self.k.delete(0, tk.END); self.k.insert(0, "400")
            self.rho.delete(0, tk.END); self.rho.insert(0, "8960")
            self.cp.delete(0, tk.END); self.cp.insert(0, "385")
        elif material == "Aluminum":
            self.k.delete(0, tk.END); self.k.insert(0, "237")
            self.rho.delete(0, tk.END); self.rho.insert(0, "2700")
            self.cp.delete(0, tk.END); self.cp.insert(0, "900")
        
    def setup_plots(self):
        """Initialize the plot area"""
        self.fig = plt.figure(figsize=(10, 6), dpi=100)
        gs = gridspec.GridSpec(2, 3, figure=self.fig, height_ratios=[2, 1], hspace=0.5, wspace=0.3)
        
        self.ax1 = self.fig.add_subplot(gs[0, 0])
        self.ax2 = self.fig.add_subplot(gs[0, 1])
        self.ax3 = self.fig.add_subplot(gs[0, 2])
        self.ax4 = self.fig.add_subplot(gs[1, :])
        
        self.fig.suptitle('Heat Transfer Analysis - Physics Corrected v8.2', fontsize=10, y=0.98)
        
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()
            ax.tick_params(labelsize=7)
        
        self.ax1.set_title('Square Bar', fontsize=9)
        self.ax2.set_title('Cylindrical Bar', fontsize=9)
        self.ax3.set_title('Conical Tip Bar', fontsize=9)
        self.ax4.set_title('Click "Start Simulation" to begin', fontsize=9)
        
        # Add axis labels
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.set_xlabel('Width/Radius (mm)', fontsize=7)
            ax.set_ylabel('Height (mm)', fontsize=7)
        
        self.ax4.set_xlabel('Time (s)', fontsize=8)
        self.ax4.set_ylabel('Temperature (°C)', fontsize=8)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def get_resolution_params(self, geometry_type):
        """Get resolution parameters based on selection"""
        resolutions = {
            'Low': {
                'square': (15, 15),
                'cylindrical': (12, 25),
                'conical': (25,)
            },
            'Medium': {
                'square': (25, 25),
                'cylindrical': (18, 35),
                'conical': (40,)
            },
            'High': {
                'square': (35, 35),
                'cylindrical': (24, 45),
                'conical': (50,)
            }
        }
        return resolutions[self.resolution_var.get()][geometry_type]
    
    def run_simulation(self):
        """Run the cooling simulation for all specimen geometries"""
        try:
            self.status_var.set("Running simulation...")
            self.root.update()
            
            # Get parameters
            h_waterjet = float(self.h_waterjet.get())
            h_natural = float(self.h_natural.get())
            T_coolant = float(self.T_coolant.get())
            T_init = float(self.T_init.get())
            sim_time = float(self.sim_time.get())
            k = float(self.k.get())
            rho = float(self.rho.get())
            cp = float(self.cp.get())
            
            # Get geometry parameters
            square_width = float(self.square_width.get()) / 1000.0
            square_height = float(self.square_height.get()) / 1000.0
            cyl_diameter = float(self.cyl_diameter.get()) / 1000.0
            cyl_height = float(self.cyl_height.get()) / 1000.0
            cone_cyl_diameter = float(self.cone_cyl_diameter.get()) / 1000.0
            cone_cyl_height = float(self.cone_cyl_height.get()) / 1000.0
            cone_tip_height = float(self.cone_tip_height.get()) / 1000.0
            cone_angle = float(self.cone_angle.get())
            
            # Run simulations
            time_sq, temp_sq = self.simulate_square_bar_fast(k, rho, cp, h_waterjet, h_natural, T_coolant, T_init, sim_time, square_width, square_height)
            time_cyl, temp_cyl = self.simulate_cylindrical_bar_fast(k, rho, cp, h_waterjet, h_natural, T_coolant, T_init, sim_time, cyl_diameter, cyl_height)
            time_cone, temp_cone = self.simulate_conical_tip_bar_fast(k, rho, cp, h_waterjet, h_natural, T_coolant, T_init, sim_time, cone_cyl_diameter, cone_cyl_height, cone_tip_height, cone_angle)
            
            # Plot thermal history
            self.ax4.clear()
            self.ax4.plot(time_sq, temp_sq, 'r-', linewidth=1.5, label='Square Bar')
            self.ax4.plot(time_cyl, temp_cyl, 'g-', linewidth=1.5, label='Cylindrical Bar')
            self.ax4.plot(time_cone, temp_cone, 'b-', linewidth=1.5, label='Conical Tip Bar')
            self.ax4.set_xlabel('Time (s)', fontsize=8)
            self.ax4.set_ylabel('Temperature (°C)', fontsize=8)
            self.ax4.set_title('Center Point Temperature vs Time', fontsize=9)
            self.ax4.legend(fontsize=7)
            self.ax4.grid(True, alpha=0.3)
            self.ax4.tick_params(labelsize=7)
            
            self.canvas.draw()
            self.status_var.set("Simulation completed!")
            
        except ValueError as e:
            self.status_var.set("Error: Check input values")
            messagebox.showerror("Input Error", f"Please check all input values are valid numbers: {e}")
        except Exception as e:
            self.status_var.set("Error in simulation")
            messagebox.showerror("Simulation Error", f"An error occurred during simulation: {e}")

    def simulate_square_bar_fast(self, k, rho, cp, h_waterjet, h_natural, T_coolant, T_init, sim_time, width, height):
        """Square bar simulation using vectorized operations"""
        nz, nx = self.get_resolution_params('square')
        
        # Ensure minimum grid size
        nz = max(3, nz)
        nx = max(3, nx)
        
        dz = height / (nz - 1)
        dx = width / (nx - 1)
        
        alpha = k / (rho * cp)
        dt = max(0.001, 0.25 * min(dx**2, dz**2) / (4 * alpha))
        
        T = np.ones((nz, nx)) * T_init
        time_history = []
        temp_history = []
        t = 0
        
        # Precompute coefficients
        rx = alpha * dt / dx**2
        rz = alpha * dt / dz**2
        
        while t < sim_time:
            T_new = T.copy()
            
            # Vectorized interior update
            if nz > 2 and nx > 2:
                T_new[1:-1, 1:-1] = T[1:-1, 1:-1] + rx * (T[1:-1, 2:] - 2*T[1:-1, 1:-1] + T[1:-1, :-2]) + \
                                     rz * (T[2:, 1:-1] - 2*T[1:-1, 1:-1] + T[:-2, 1:-1])
            
            # Boundary conditions
            # Waterjet at bottom
            if nz > 1:
                T_new[0, :] = T[0, :] + 2 * rz * (T[1, :] - T[0, :] - (h_waterjet * dz/k) * (T[0, :] - T_coolant))
            
            # Natural convection on sides
            if nx > 2:
                T_new[1:-1, 0] = T[1:-1, 0] + 2 * rx * (T[1:-1, 1] - T[1:-1, 0] - (h_natural * dx/k) * (T[1:-1, 0] - T_coolant))
                T_new[1:-1, -1] = T[1:-1, -1] + 2 * rx * (T[1:-1, -2] - T[1:-1, -1] - (h_natural * dx/k) * (T[1:-1, -1] - T_coolant))
            
            # Natural convection on top
            if nz > 2:
                T_new[-1, 1:-1] = T[-1, 1:-1] + 2 * rz * (T[-2, 1:-1] - T[-1, 1:-1] - (h_natural * dz/k) * (T[-1, 1:-1] - T_coolant))
            
            T = T_new
            t += dt
            
            if len(time_history) == 0 or t - time_history[-1] >= 0.5:
                time_history.append(t)
                center_z = min(nz//2, nz-1)
                center_x = min(nx//2, nx-1)
                temp_history.append(T[center_z, center_x])
        
        # Plot with custom geometry info
        self.ax1.clear()
        im = self.ax1.imshow(T, extent=[0, width*1000, 0, height*1000], origin='lower', 
                            cmap=self.cmap, vmin=T_coolant, vmax=T_init)
        self.ax1.set_title(f'Square Bar\n{width*1000:.1f}×{height*1000:.1f}mm\nFinal: {T[nz//2, nx//2]:.0f}°C', fontsize=8)
        self.ax1.set_xlabel('Width (mm)', fontsize=7)
        self.ax1.set_ylabel('Height (mm)', fontsize=7)
        self.ax1.tick_params(labelsize=6)
        
        # Add/update colorbar
        if self.colorbar is None:
            self.colorbar = self.fig.colorbar(im, ax=self.ax1, shrink=0.8)
            self.colorbar.set_label('Temperature (°C)', fontsize=8)
        else:
            self.colorbar.update_normal(im)
        
        self.ax1.add_patch(Rectangle((1, -2), width*1000-2, 2, fill=True, color='blue', alpha=0.3))
        self.ax1.text(width*500, -1, 'Waterjet', ha='center', va='bottom', color='blue', fontsize=6)
        
        return time_history, temp_history

    def simulate_cylindrical_bar_fast(self, k, rho, cp, h_waterjet, h_natural, T_coolant, T_init, sim_time, diameter, height):
        """CORRECTED Cylindrical bar simulation with proper physics"""
        radius = diameter / 2.0
        
        # Use reasonable resolution
        nr, nz = self.get_resolution_params('cylindrical')
        
        # Ensure minimum grid size
        nr = max(3, nr)
        nz = max(3, nz)
            
        dr = radius / (nr - 1)
        dz = height / (nz - 1)
        
        alpha = k / (rho * cp)
        
        # Conservative time step for stability
        dt = 0.1 * min(dr**2, dz**2) / (4 * alpha)
        dt = max(0.001, min(dt, 0.1))
        
        T = np.ones((nr, nz)) * T_init
        time_history = []
        temp_history = []
        t = 0
        
        # Precompute radial positions (avoid division by zero)
        r = np.linspace(0, radius, nr)
        r_safe = r.copy()
        r_safe[0] = dr * 0.5  # Small value for center point
        
        while t < sim_time:
            T_new = T.copy()
            
            # Interior points using proper cylindrical coordinates
            for i in range(1, nr-1):
                for j in range(1, nz-1):
                    r_val = r_safe[i]
                    
                    # Radial derivatives
                    dT_dr = (T[i+1, j] - T[i-1, j]) / (2 * dr)
                    d2T_dr2 = (T[i+1, j] - 2*T[i, j] + T[i-1, j]) / (dr**2)
                    
                    # Axial derivatives
                    d2T_dz2 = (T[i, j+1] - 2*T[i, j] + T[i, j-1]) / (dz**2)
                    
                    # Cylindrical heat equation: ∂T/∂t = α(∂²T/∂r² + (1/r)∂T/∂r + ∂²T/∂z²)
                    T_new[i, j] = T[i, j] + alpha * dt * (d2T_dr2 + (1/r_val)*dT_dr + d2T_dz2)
            
            # Centerline (r=0) - use symmetry condition
            for j in range(1, nz-1):
                # At r=0, use: ∂²T/∂r² + (1/r)∂T/∂r → 2∂²T/∂r² by L'Hopital's rule
                d2T_dr2_center = 2 * (T[1, j] - T[0, j]) / (dr**2)
                d2T_dz2 = (T[0, j+1] - 2*T[0, j] + T[0, j-1]) / (dz**2)
                T_new[0, j] = T[0, j] + alpha * dt * (d2T_dr2_center + d2T_dz2)
            
            # BOUNDARY CONDITIONS - PHYSICALLY CORRECT
            
            # Bottom surface (z=0) - Waterjet cooling
            for i in range(nr):
                # Convective boundary: -k(∂T/∂z) = h_waterjet(T - T_coolant)
                # Use forward difference for derivative at boundary
                dT_dz = (T[i, 1] - T[i, 0]) / dz
                T_new[i, 0] = T[i, 0] + alpha * dt * (
                    (T[i, 1] - T[i, 0]) / dz**2 +  # Conduction in z-direction
                    h_waterjet * (T_coolant - T[i, 0]) / (k * dz)  # Convection
                )
            
            # Top surface (z=height) - Natural convection
            for i in range(nr):
                # Convective boundary: -k(∂T/∂z) = h_natural(T - T_coolant)
                dT_dz = (T[i, -1] - T[i, -2]) / dz
                T_new[i, -1] = T[i, -1] + alpha * dt * (
                    (T[i, -2] - T[i, -1]) / dz**2 +  # Conduction in z-direction
                    h_natural * (T_coolant - T[i, -1]) / (k * dz)  # Convection
                )
            
            # Outer surface (r=radius) - Natural convection
            for j in range(1, nz-1):
                # Convective boundary: -k(∂T/∂r) = h_natural(T - T_coolant)
                dT_dr = (T[-1, j] - T[-2, j]) / dr
                T_new[-1, j] = T[-1, j] + alpha * dt * (
                    (T[-2, j] - T[-1, j]) / dr**2 +  # Conduction in r-direction
                    (1/radius) * dT_dr +  # Cylindrical term
                    h_natural * (T_coolant - T[-1, j]) / (k * dr)  # Convection
                )
            
            T = np.copy(T_new)
            t += dt
            
            # Record data less frequently for performance
            if len(time_history) == 0 or t - time_history[-1] >= 0.5:
                time_history.append(t)
                center_r = min(nr//2, nr-1)
                center_z = min(nz//2, nz-1)
                temp_history.append(T[center_r, center_z])
                
            # Early termination if simulation is stable but not progressing
            if t > 10 and len(temp_history) > 1 and abs(temp_history[-1] - temp_history[-2]) < 0.1:
                if temp_history[-1] < T_coolant + 50:  # Nearly cooled
                    break
        
        # Plot
        self.ax2.clear()
        z = np.linspace(0, height, nz)
        r_plot = np.linspace(0, radius, nr)
        Z, R = np.meshgrid(z, r_plot)
        
        im = self.ax2.contourf(R*1000, Z*1000, T, levels=20, cmap=self.cmap, vmin=T_coolant, vmax=T_init)
        self.ax2.set_title(f'Cylindrical Bar\nØ{diameter*1000:.1f}mm × {height*1000:.1f}mm\nFinal: {T[nr//2, nz//2]:.0f}°C', fontsize=8)
        self.ax2.set_xlabel('Radius (mm)', fontsize=7)
        self.ax2.set_ylabel('Height (mm)', fontsize=7)
        self.ax2.set_aspect('equal')
        self.ax2.tick_params(labelsize=6)
        
        # Add/update colorbar
        if self.colorbar is None:
            self.colorbar = self.fig.colorbar(im, ax=self.ax2, shrink=0.8)
            self.colorbar.set_label('Temperature (°C)', fontsize=8)
        else:
            self.colorbar.update_normal(im)
        
        self.ax2.add_patch(Rectangle((-radius*1200, -2), 2*radius*1200, 2, fill=True, color='blue', alpha=0.3))
        self.ax2.text(0, -1, 'Waterjet', ha='center', va='bottom', color='blue', fontsize=6)
        
        return time_history, temp_history

    def simulate_conical_tip_bar_fast(self, k, rho, cp, h_waterjet, h_natural, T_coolant, T_init, sim_time, cyl_diameter, cyl_height, cone_height, cone_angle):
        """Conical tip bar simulation"""
        total_length = cyl_height + cone_height
        radius_cyl = cyl_diameter / 2.0
        
        n_points = self.get_resolution_params('conical')[0]
        n_points = max(3, n_points)
        dx = total_length / (n_points - 1)
        
        alpha = k / (rho * cp)
        dt = max(0.001, 0.3 * dx**2 / (4 * alpha))
        
        x = np.linspace(0, total_length, n_points)
        T = np.ones(n_points) * T_init
        
        time_history = []
        temp_history = []
        t = 0
        
        while t < sim_time:
            T_new = T.copy()
            
            # 1D heat equation
            if n_points > 2:
                d2T_dx2 = (T[2:] - 2*T[1:-1] + T[:-2]) / dx**2
                T_new[1:-1] = T[1:-1] + alpha * dt * d2T_dx2
            
            # Boundary conditions
            T_new[0] = T[0] - alpha * dt * (h_natural / (k * dx)) * (T[0] - T_coolant)
            T_new[-1] = T_coolant + (T[-1] - T_coolant) * np.exp(-h_waterjet * dx / k)
            
            # Natural convection along length
            if n_points > 2:
                T_new[1:-1] -= alpha * dt * (h_natural / (k * dx)) * (T[1:-1] - T_coolant)
            
            T = T_new
            t += dt
            
            if len(time_history) == 0 or t - time_history[-1] >= 0.5:
                time_history.append(t)
                center_idx = min(n_points//2, n_points-1)
                temp_history.append(T[center_idx])
        
        # Plot
        self.ax3.clear()
        cone_start_idx = int(cyl_height / total_length * n_points)
        
        y_cyl = np.ones(cone_start_idx) * radius_cyl * 1000
        cone_max_radius = np.tan(np.radians(cone_angle)) * cone_height
        y_cone = cone_max_radius * 1000 * (1 - np.linspace(0, 1, n_points - cone_start_idx))
        y_full = np.concatenate([y_cyl, y_cone])
        
        for i in range(len(x)-1):
            color_val = (T[i] - T_coolant) / (T_init - T_coolant)
            color = self.cmap(color_val)
            self.ax3.fill_between([x[i]*1000, x[i+1]*1000], -y_full[i], y_full[i], color=color, alpha=0.8)
        
        self.ax3.set_xlim(0, total_length * 1000)
        self.ax3.set_ylim(-max(y_full)*1.2, max(y_full)*1.2)
        self.ax3.set_title(f'Conical Tip Bar\nØ{cyl_diameter*1000:.1f}mm + {cone_height*1000:.1f}mm cone\nFinal: {T[n_points//2]:.0f}°C', fontsize=8)
        self.ax3.set_xlabel('Height (mm)', fontsize=7)
        self.ax3.set_ylabel('Radius (mm)', fontsize=7)
        self.ax3.set_aspect('equal')
        self.ax3.tick_params(labelsize=6)
        
        # Create scalar mappable for colorbar
        norm = Normalize(vmin=T_coolant, vmax=T_init)
        sm = ScalarMappable(norm=norm, cmap=self.cmap)
        sm.set_array([])
        
        # Add/update colorbar
        if self.colorbar is None:
            self.colorbar = self.fig.colorbar(sm, ax=self.ax3, shrink=0.8)
            self.colorbar.set_label('Temperature (°C)', fontsize=8)
        else:
            self.colorbar.update_normal(sm)
        
        tip_x = total_length * 1000
        self.ax3.add_patch(Rectangle((tip_x-1, -max(y_full)), 2, 2*max(y_full), 
                                   fill=True, color='blue', alpha=0.3))
        self.ax3.text(tip_x, 0, 'Waterjet', ha='center', va='center', color='blue', fontsize=6)
        
        return time_history, temp_history

def main():
    root = tk.Tk()
    app = HeatTransferSimulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
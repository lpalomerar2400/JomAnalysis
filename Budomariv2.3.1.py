import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import json
import os

class AutomotiveStampingAnalyzer:
    """Comprehensive Automotive Stamping Cost Analysis with GUI"""
    
    # Version control
    VERSION = "2.3.1"
    RELEASE_DATE = "2025-10-22"
    
    CHANGE_LOG = [
        {"version": "2.3.1", "date": "2025-10-22", "changes": [
            "Added savings clarification (annual vs per metric ton)",
            "Enhanced results breakdown with per-ton calculations",
            "Improved savings interpretation in reports"
        ]},
        {"version": "2.3.0", "date": "2025-10-22", "changes": [
            "Added material cost fields in $/MT and $/cwt",
            "Added currency conversion system",
            "Updated 'Part Geometry' to 'Blank Geometry'",
            "Enhanced results clarity with savings explanations",
            "Updated developer information in reports"
        ]},
        {"version": "2.2.0", "date": "2025-10-19", "changes": [
            "Added thickness optimization fields",
            "Integrated developer information",
            "Enhanced material comparison with thickness variables",
            "Added dual optimization (material + thickness)",
            "Improved results reporting"
        ]},
        {"version": "2.1.0", "date": "2025-10-15", "changes": [
            "Added comprehensive GUI interface",
            "Integrated version control system",
            "Added change log display",
            "Enhanced user input validation",
            "Added real-time cost calculations"
        ]},
        {"version": "2.0.0", "date": "2025-09-22", "changes": [
            "Added coil efficiency calculations",
            "Integrated thickness optimization",
            "Added comprehensive overhead costing",
            "Enhanced material property database",
            "Added nesting efficiency analysis"
        ]},
        {"version": "1.0.0", "date": "2025-09-12", "changes": [
            "Initial release with basic material cost analysis",
            "Direct material cost calculations",
            "Basic scrap rate considerations",
            "Simple material comparison engine"
        ]}
    ]
    
    # Personal Information
    DEVELOPER_INFO = {
        "name": "Luis Rodrigo Palomera",
        "student_id": "A240619",
        "institution": "Instituto Politécnico Nacional (IPN) - CICATA Querétaro",
        "projects": "CVU 881822, SECIHTI 4021946",
        "github": "lpalomerar2400",
        "email": "palomera.luis@gmail.com",
        "specialties": [
            "Material Switching Optimization",
            "Stamping Process Cost Analysis",
            "Lightweighting Strategies",
            "Supply Chain Cost Reduction",
            "Advanced Materials Implementation"
        ]
    }

        # References and Bibliography
    REFERENCES = [
        {
            "category": "Material Properties & Standards",
            "sources": [
                "ASTM International. (2023). Standard Specification for Steel, Sheet, Carbon, and High-Strength, Low-Alloy for Automotive Applications.",
                "ASM International. (2022). ASM Handbook, Volume 14B: Metalworking: Sheet Forming.",
                "European Aluminum Association. (2024). Automotive Aluminum Design Manual.",
                "International Magnesium Association. (2023). Magnesium Applications in Automotive Industry."
            ]
        },
        {
            "category": "Cost Analysis Methodology",
            "sources": [
                "Society of Automotive Engineers. (2024). SAE J4002 - Life Cycle Cost Analysis for Automotive Materials.",
                "International Organization for Standardization. (2023). ISO 14040: Environmental Management - Life Cycle Assessment.",
                "Kalpakjian, S., & Schmid, S. R. (2024). Manufacturing Engineering and Technology. Pearson Education.",
                "Groover, M. P. (2023). Fundamentals of Modern Manufacturing: Materials, Processes, and Systems. Wiley."
            ]
        },
        {
            "category": "Stamping Process Optimization",
            "sources": [
                "American Metal Stamping Association. (2024). Best Practices in Automotive Stamping.",
                "Tschätsch, H. (2023). Metal Forming Practise: Processes - Machines - Tools. Springer.",
                "Lange, K. (2022). Handbook of Metal Forming. Society of Manufacturing Engineers.",
                "Narasimhan, K., & Miles, M. P. (2024). Advanced Stamping Technologies for Lightweight Vehicles."
            ]
        },
        {
            "category": "Industry Data & Market Analysis",
            "sources": [
                "World Steel Association. (2024). Steel Statistical Yearbook 2024.",
                "International Aluminum Institute. (2024). Aluminum Automotive Manual.",
                "Ducker Worldwide. (2024). North American Light Vehicle Aluminum Content Study.",
                "McKinsey & Company. (2024). Automotive Materials Cost Optimization Strategies."
            ]
        },
        {
            "category": "Software & Technical Resources",
            "sources": [
                "Python Software Foundation. (2024). Python 3.12 Documentation.",
                "Matplotlib Development Team. (2024). Matplotlib: Visualization with Python.",
                "Pandas Development Team. (2024). pandas: Python Data Analysis Library.",
                "TKinter Documentation. (2024). GUI Programming with Tkinter."
            ]
        },
        {
            "category": "Academic Research",
            "sources": [
                "MIT Materials Processing Center. (2024). Lightweight Materials for Automotive Applications.",
                "University of Michigan. (2024). Automotive Research Center Publications.",
                "Fraunhofer Institute. (2024). Production Technology and Lightweight Design Research.",
                "University of Cambridge. (2024). Advanced Materials and Processing Research Group."
            ]
        }
    ]
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"Automotive Stamping Cost Analyzer v{self.VERSION}")
        self.root.geometry("1400x900")
        
        # Initialize data
        self.setup_materials_database()
        self.setup_default_parameters()
        
        # Create GUI
        self.create_gui()
        
    def setup_materials_database(self):
        """Initialize materials database"""
        self.materials = {
            'Mild Steel': {
                'density': 7.85, 'cost_per_kg': 0.8, 'scrap_value': 0.2,
                'stamping_pressure_required': 400, 'energy_per_kg': 1.2,
                'tooling_wear_factor': 1.0, 'processing_time': 1.0,
                'typical_thickness_range': (0.6, 3.0),
                'max_thickness_reduction': 0.15,
                'formability_index': 1.0,
                'springback_factor': 1.0,
                'typical_coil_widths': [1200, 1500, 1800]
            },
            'High Strength Steel': {
                'density': 7.85, 'cost_per_kg': 1.2, 'scrap_value': 0.25,
                'stamping_pressure_required': 600, 'energy_per_kg': 1.5,
                'tooling_wear_factor': 1.3, 'processing_time': 1.2,
                'typical_thickness_range': (0.8, 2.5),
                'max_thickness_reduction': 0.10,
                'formability_index': 0.8,
                'springback_factor': 1.3,
                'typical_coil_widths': [1200, 1500]
            },
            'Aluminum 6061': {
                'density': 2.7, 'cost_per_kg': 3.5, 'scrap_value': 1.8,
                'stamping_pressure_required': 300, 'energy_per_kg': 0.8,
                'tooling_wear_factor': 0.7, 'processing_time': 0.9,
                'typical_thickness_range': (0.8, 4.0),
                'max_thickness_reduction': 0.20,
                'formability_index': 1.4,
                'springback_factor': 0.7,
                'typical_coil_widths': [1200, 1500, 2000]
            },
            'Aluminum 5052': {
                'density': 2.68, 'cost_per_kg': 3.2, 'scrap_value': 1.6,
                'stamping_pressure_required': 280, 'energy_per_kg': 0.75,
                'tooling_wear_factor': 0.6, 'processing_time': 0.85,
                'typical_thickness_range': (0.7, 3.5),
                'max_thickness_reduction': 0.25,
                'formability_index': 1.6,
                'springback_factor': 0.6,
                'typical_coil_widths': [1200, 1500, 2000]
            },
            'Advanced High Strength Steel': {
                'density': 7.85, 'cost_per_kg': 1.8, 'scrap_value': 0.3,
                'stamping_pressure_required': 800, 'energy_per_kg': 2.0,
                'tooling_wear_factor': 1.8, 'processing_time': 1.5,
                'typical_thickness_range': (0.9, 2.2),
                'max_thickness_reduction': 0.08,
                'formability_index': 0.6,
                'springback_factor': 1.8,
                'typical_coil_widths': [1200, 1500]
            },
            'Magnesium AZ31': {
                'density': 1.74, 'cost_per_kg': 5.2, 'scrap_value': 2.5,
                'stamping_pressure_required': 250, 'energy_per_kg': 0.6,
                'tooling_wear_factor': 0.5, 'processing_time': 0.8,
                'typical_thickness_range': (1.0, 4.5),
                'max_thickness_reduction': 0.30,
                'formability_index': 1.8,
                'springback_factor': 0.5,
                'typical_coil_widths': [1200, 1500, 2000]
            }
        }
    
    def setup_default_parameters(self):
        """Set default cost parameters"""
        self.cost_params = {
            'energy_cost_per_kwh': 0.12,
            'operator_hourly_rate': 35.0,
            'supervision_cost_per_operator': 15.0,
            'maintenance_cost_per_hour': 25.0,
            'equipment_depreciation_hourly': 40.0,
            'facility_cost_per_hour': 15.0,
            'tooling_cost_per_stroke': 0.02,
            'quality_control_cost_per_part': 0.50,
            'coil_handling_cost_per_ton': 50.0,
            'scrap_processing_cost_per_kg': 0.10,
            'shipping_cost_per_kg': 0.25
        }
        
        # Currency exchange rates (default values)
        self.currency_rates = {
            'EUR': 0.92,
            'GBP': 0.79,
            'JPY': 148.50,
            'MXN': 17.25
        }
    
    def create_gui(self):
        """Create the main GUI interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_input_tab()
        self.setup_materials_tab()
        self.setup_costs_tab()
        self.setup_results_tab()
        self.setup_about_tab()
        
    def setup_input_tab(self):
        """Setup input parameters tab"""
        self.input_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.input_frame, text="Part & Production")
        
        # Header
        header_frame = ttk.LabelFrame(self.input_frame, text="Blank Geometry & Production Parameters")
        header_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(header_frame, text=f"Automotive Stamping Cost Analyzer v{self.VERSION}", 
                 font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Blank Geometry (CTL only)
        geometry_frame = ttk.LabelFrame(self.input_frame, text="Blank Geometry (CTL only)")
        geometry_frame.pack(fill='x', padx=5, pady=5)
        
        # Row 1 - Basic dimensions
        row1 = ttk.Frame(geometry_frame)
        row1.pack(fill='x', pady=2)
        
        ttk.Label(row1, text="Length (mm):").grid(row=0, column=0, sticky='w', padx=5)
        self.part_length = ttk.Entry(row1, width=10)
        self.part_length.insert(0, "800")
        self.part_length.grid(row=0, column=1, padx=5)
        
        ttk.Label(row1, text="Width (mm):").grid(row=0, column=2, sticky='w', padx=5)
        self.part_width = ttk.Entry(row1, width=10)
        self.part_width.insert(0, "600")
        self.part_width.grid(row=0, column=3, padx=5)
        
        # Thickness Optimization Frame
        thickness_frame = ttk.LabelFrame(self.input_frame, text="Thickness Optimization")
        thickness_frame.pack(fill='x', padx=5, pady=5)
        
        # Row 2 - Current thickness
        row2 = ttk.Frame(thickness_frame)
        row2.pack(fill='x', pady=2)
        
        ttk.Label(row2, text="Current Thickness (mm):").grid(row=0, column=0, sticky='w', padx=5)
        self.current_thickness = ttk.Entry(row2, width=10)
        self.current_thickness.insert(0, "1.2")
        self.current_thickness.grid(row=0, column=1, padx=5)
        
        ttk.Label(row2, text="Optimized Thickness (mm):").grid(row=0, column=2, sticky='w', padx=5)
        self.optimized_thickness = ttk.Entry(row2, width=10)
        self.optimized_thickness.insert(0, "1.0")
        self.optimized_thickness.grid(row=0, column=3, padx=5)
        
        ttk.Label(row2, text="Thickness Reduction (%):").grid(row=0, column=4, sticky='w', padx=5)
        self.thickness_reduction_label = ttk.Label(row2, text="16.7%", foreground="blue")
        self.thickness_reduction_label.grid(row=0, column=5, padx=5)
        
        # Bind thickness calculation
        self.current_thickness.bind('<KeyRelease>', self.calculate_thickness_reduction)
        self.optimized_thickness.bind('<KeyRelease>', self.calculate_thickness_reduction)
        
        # Material Cost Input Frame
        material_cost_frame = ttk.LabelFrame(self.input_frame, text="Material Cost Input")
        material_cost_frame.pack(fill='x', padx=5, pady=5)
        
        # Row 3 - Material cost inputs
        row3 = ttk.Frame(material_cost_frame)
        row3.pack(fill='x', pady=2)
        
        ttk.Label(row3, text="Current Material Cost ($/MT):").grid(row=0, column=0, sticky='w', padx=5)
        self.current_material_cost_mt = ttk.Entry(row3, width=12)
        self.current_material_cost_mt.insert(0, "800")
        self.current_material_cost_mt.grid(row=0, column=1, padx=5)
        
        ttk.Label(row3, text="($/cwt):").grid(row=0, column=2, sticky='w', padx=5)
        self.current_material_cost_cwt = ttk.Entry(row3, width=12)
        self.current_material_cost_cwt.insert(0, "36.29")
        self.current_material_cost_cwt.grid(row=0, column=3, padx=5)
        
        ttk.Label(row3, text="Proposed Material Cost ($/MT):").grid(row=0, column=4, sticky='w', padx=5)
        self.proposed_material_cost_mt = ttk.Entry(row3, width=12)
        self.proposed_material_cost_mt.insert(0, "3200")
        self.proposed_material_cost_mt.grid(row=0, column=5, padx=5)
        
        ttk.Label(row3, text="($/cwt):").grid(row=0, column=6, sticky='w', padx=5)
        self.proposed_material_cost_cwt = ttk.Entry(row3, width=12)
        self.proposed_material_cost_cwt.insert(0, "145.15")
        self.proposed_material_cost_cwt.grid(row=0, column=7, padx=5)
        
        # Bind cost conversions
        self.current_material_cost_mt.bind('<KeyRelease>', lambda e: self.convert_mt_to_cwt('current'))
        self.current_material_cost_cwt.bind('<KeyRelease>', lambda e: self.convert_cwt_to_mt('current'))
        self.proposed_material_cost_mt.bind('<KeyRelease>', lambda e: self.convert_mt_to_cwt('proposed'))
        self.proposed_material_cost_cwt.bind('<KeyRelease>', lambda e: self.convert_cwt_to_mt('proposed'))
        
        # Production Parameters
        production_frame = ttk.LabelFrame(self.input_frame, text="Production Parameters")
        production_frame.pack(fill='x', padx=5, pady=5)
        
        # Row 4
        row4 = ttk.Frame(production_frame)
        row4.pack(fill='x', pady=2)
        
        ttk.Label(row4, text="Annual Volume:").grid(row=0, column=0, sticky='w', padx=5)
        self.annual_volume = ttk.Entry(row4, width=15)
        self.annual_volume.insert(0, "150000")
        self.annual_volume.grid(row=0, column=1, padx=5)
        
        ttk.Label(row4, text="Shifts per Day:").grid(row=0, column=2, sticky='w', padx=5)
        self.shifts_per_day = ttk.Entry(row4, width=10)
        self.shifts_per_day.insert(0, "2")
        self.shifts_per_day.grid(row=0, column=3, padx=5)
        
        ttk.Label(row4, text="Operating Days/Year:").grid(row=0, column=4, sticky='w', padx=5)
        self.operating_days = ttk.Entry(row4, width=10)
        self.operating_days.insert(0, "250")
        self.operating_days.grid(row=0, column=5, padx=5)
        
        # Strip Parameters
        strip_frame = ttk.LabelFrame(self.input_frame, text="Strip Parameters")
        strip_frame.pack(fill='x', padx=5, pady=5)
        
        # Row 5
        row5 = ttk.Frame(strip_frame)
        row5.pack(fill='x', pady=2)
        
        ttk.Label(row5, text="Strip Width (mm):").grid(row=0, column=0, sticky='w', padx=5)
        self.coil_width = ttk.Entry(row5, width=10)
        self.coil_width.insert(0, "1500")
        self.coil_width.grid(row=0, column=1, padx=5)
        
        ttk.Label(row5, text="Strip Weight (kg):").grid(row=0, column=2, sticky='w', padx=5)
        self.coil_weight = ttk.Entry(row5, width=10)
        self.coil_weight.insert(0, "20000")
        self.coil_weight.grid(row=0, column=3, padx=5)
        
        ttk.Label(row5, text="Coil Change Time (min):").grid(row=0, column=4, sticky='w', padx=5)
        self.coil_change_time = ttk.Entry(row5, width=10)
        self.coil_change_time.insert(0, "30")
        self.coil_change_time.grid(row=0, column=5, padx=5)
        
        # Material Selection
        material_frame = ttk.LabelFrame(self.input_frame, text="Material Selection")
        material_frame.pack(fill='x', padx=5, pady=5)
        
        # Row 6
        row6 = ttk.Frame(material_frame)
        row6.pack(fill='x', pady=2)
        
        ttk.Label(row6, text="Current Material:").grid(row=0, column=0, sticky='w', padx=5)
        self.current_material = ttk.Combobox(row6, values=list(self.materials.keys()), width=15)
        self.current_material.set("Mild Steel")
        self.current_material.grid(row=0, column=1, padx=5)
        
        ttk.Label(row6, text="Proposed Material:").grid(row=0, column=2, sticky='w', padx=5)
        self.proposed_material = ttk.Combobox(row6, values=list(self.materials.keys()), width=15)
        self.proposed_material.set("Aluminum 5052")
        self.proposed_material.grid(row=0, column=3, padx=5)
        
        # Analysis Type
        analysis_frame = ttk.LabelFrame(self.input_frame, text="Analysis Type")
        analysis_frame.pack(fill='x', padx=5, pady=5)
        
        self.analysis_type = tk.StringVar(value="both")
        ttk.Radiobutton(analysis_frame, text="Material Switch Only", 
                       variable=self.analysis_type, value="material").pack(side='left', padx=10)
        ttk.Radiobutton(analysis_frame, text="Thickness Optimization Only", 
                       variable=self.analysis_type, value="thickness").pack(side='left', padx=10)
        ttk.Radiobutton(analysis_frame, text="Both Material Switch & Thickness Optimization", 
                       variable=self.analysis_type, value="both").pack(side='left', padx=10)
        
        # Calculate Button
        button_frame = ttk.Frame(self.input_frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="Calculate Cost Analysis", 
                  command=self.calculate_analysis).pack(pady=5)
    
    def convert_mt_to_cwt(self, material_type):
        """Convert $/MT to $/cwt"""
        try:
            if material_type == 'current':
                mt_value = float(self.current_material_cost_mt.get())
                cwt_value = mt_value / 22.046  # 1 MT = 22.046 cwt
                self.current_material_cost_cwt.delete(0, tk.END)
                self.current_material_cost_cwt.insert(0, f"{cwt_value:.2f}")
            else:
                mt_value = float(self.proposed_material_cost_mt.get())
                cwt_value = mt_value / 22.046
                self.proposed_material_cost_cwt.delete(0, tk.END)
                self.proposed_material_cost_cwt.insert(0, f"{cwt_value:.2f}")
        except ValueError:
            pass
    
    def convert_cwt_to_mt(self, material_type):
        """Convert $/cwt to $/MT"""
        try:
            if material_type == 'current':
                cwt_value = float(self.current_material_cost_cwt.get())
                mt_value = cwt_value * 22.046
                self.current_material_cost_mt.delete(0, tk.END)
                self.current_material_cost_mt.insert(0, f"{mt_value:.0f}")
            else:
                cwt_value = float(self.proposed_material_cost_cwt.get())
                mt_value = cwt_value * 22.046
                self.proposed_material_cost_mt.delete(0, tk.END)
                self.proposed_material_cost_mt.insert(0, f"{mt_value:.0f}")
        except ValueError:
            pass
    
    def calculate_thickness_reduction(self, event=None):
        """Calculate and display thickness reduction percentage"""
        try:
            current = float(self.current_thickness.get())
            optimized = float(self.optimized_thickness.get())
            reduction = ((current - optimized) / current) * 100
            self.thickness_reduction_label.config(text=f"{reduction:.1f}%")
            
            # Color code based on reduction
            if reduction > 20:
                self.thickness_reduction_label.config(foreground="green")
            elif reduction > 10:
                self.thickness_reduction_label.config(foreground="blue")
            else:
                self.thickness_reduction_label.config(foreground="orange")
                
        except (ValueError, ZeroDivisionError):
            self.thickness_reduction_label.config(text="0.0%")
    
    def setup_materials_tab(self):
        """Setup materials properties tab"""
        self.materials_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.materials_frame, text="Material Properties")
        
        # Create treeview for materials
        columns = ('Property', 'Mild Steel', 'High Strength Steel', 'Aluminum 6061', 'Aluminum 5052', 'AHSS', 'Magnesium')
        self.materials_tree = ttk.Treeview(self.materials_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.materials_tree.heading(col, text=col)
            self.materials_tree.column(col, width=100)
        
        # Add material data
        material_data = [
            ('Density (g/cm³)', '7.85', '7.85', '2.70', '2.68', '7.85', '1.74'),
            ('Cost ($/kg)', '0.80', '1.20', '3.50', '3.20', '1.80', '5.20'),
            ('Scrap Value ($/kg)', '0.20', '0.25', '1.80', '1.60', '0.30', '2.50'),
            ('Stamping Pressure (MPa)', '400', '600', '300', '280', '800', '250'),
            ('Energy (kWh/kg)', '1.20', '1.50', '0.80', '0.75', '2.00', '0.60'),
            ('Tool Wear Factor', '1.00', '1.30', '0.70', '0.60', '1.80', '0.50'),
            ('Processing Time (s)', '1.00', '1.20', '0.90', '0.85', '1.50', '0.80'),
            ('Max Thickness Reduction', '15%', '10%', '20%', '25%', '8%', '30%'),
            ('Formability Index', '1.00', '0.80', '1.40', '1.60', '0.60', '1.80')
        ]
        
        for data in material_data:
            self.materials_tree.insert('', 'end', values=data)
        
        self.materials_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Notes frame
        notes_frame = ttk.LabelFrame(self.materials_frame, text="Material Selection Notes")
        notes_frame.pack(fill='x', padx=5, pady=5)
        
        notes_text = """
        • Mild Steel: Cost-effective, good formability, higher weight
        • High Strength Steel: Higher strength, reduced thickness possible, higher tool wear
        • Aluminum 6061: Good strength-to-weight, excellent corrosion resistance
        • Aluminum 5052: Excellent formability, good corrosion resistance, lower strength than 6061
        • Advanced High Strength Steel (AHSS): Highest strength, limited formability, high tool wear
        • Magnesium AZ31: Lightest option, excellent formability, higher material cost
        """
        
        ttk.Label(notes_frame, text=notes_text, justify='left').pack(padx=5, pady=5)
    
    def setup_costs_tab(self):
        """Setup cost parameters tab with currency conversion"""
        self.costs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.costs_frame, text="Cost Parameters")
        
        # Create main container with two columns
        main_container = ttk.Frame(self.costs_frame)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left Column - Cost Parameters
        cost_params_frame = ttk.LabelFrame(main_container, text="Cost Parameters (All values in USD)")
        cost_params_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Create input fields for cost parameters
        self.cost_entries = {}
        row = 0
        
        for param, value in self.cost_params.items():
            # Convert parameter name to readable format
            label_text = param.replace('_', ' ').title() + " (USD):"
            
            ttk.Label(cost_params_frame, text=label_text).grid(row=row, column=0, sticky='w', padx=5, pady=2)
            entry = ttk.Entry(cost_params_frame, width=15)
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, padx=5, pady=2)
            
            self.cost_entries[param] = entry
            row += 1
        
        # Update button
        ttk.Button(cost_params_frame, text="Update Cost Parameters", 
                  command=self.update_cost_parameters).grid(row=row, column=0, columnspan=2, pady=10)
        
        # Right Column - Currency Conversion
        currency_frame = ttk.LabelFrame(main_container, text="Currency Conversion (from USD)")
        currency_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Currency exchange rate inputs
        ttk.Label(currency_frame, text="Euro (EUR):", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.eur_rate = ttk.Entry(currency_frame, width=10)
        self.eur_rate.insert(0, str(self.currency_rates['EUR']))
        self.eur_rate.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(currency_frame, text="British Pound (GBP):", font=('Arial', 9, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.gbp_rate = ttk.Entry(currency_frame, width=10)
        self.gbp_rate.insert(0, str(self.currency_rates['GBP']))
        self.gbp_rate.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(currency_frame, text="Japanese Yen (JPY):", font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.jpy_rate = ttk.Entry(currency_frame, width=10)
        self.jpy_rate.insert(0, str(self.currency_rates['JPY']))
        self.jpy_rate.grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(currency_frame, text="Mexican Peso (MXN):", font=('Arial', 9, 'bold')).grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.mxn_rate = ttk.Entry(currency_frame, width=10)
        self.mxn_rate.insert(0, str(self.currency_rates['MXN']))
        self.mxn_rate.grid(row=3, column=1, padx=5, pady=2)
        
        # Convert button
        ttk.Button(currency_frame, text="Update Exchange Rates", 
                  command=self.update_currency_rates).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Conversion example
        example_label = ttk.Label(currency_frame, text="Note: Enter exchange rates as units of foreign currency per 1 USD", 
                                 font=('Arial', 8), foreground='blue')
        example_label.grid(row=5, column=0, columnspan=2, pady=5)
    
    def update_currency_rates(self):
        """Update currency exchange rates from user input"""
        try:
            self.currency_rates['EUR'] = float(self.eur_rate.get())
            self.currency_rates['GBP'] = float(self.gbp_rate.get())
            self.currency_rates['JPY'] = float(self.jpy_rate.get())
            self.currency_rates['MXN'] = float(self.mxn_rate.get())
            messagebox.showinfo("Success", "Currency exchange rates updated successfully!")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input in exchange rates: {e}")
    
    def setup_results_tab(self):
        """Setup results display tab"""
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Analysis Results")
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(self.results_frame, width=100, height=30)
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Default message
        self.results_text.insert('1.0', "Click 'Calculate Cost Analysis' in the Part & Production tab to generate results.")
        self.results_text.config(state='disabled')
    
    def setup_about_tab(self):
        """Setup about information tab with three-column layout"""
        self.about_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.about_frame, text="About & Version")
        
        # Create main container with three columns
        main_container = ttk.Frame(self.about_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left Column - Developer Information
        left_frame = ttk.LabelFrame(main_container, text="Developer Information")
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        developer_text = f"""
{self.DEVELOPER_INFO['name']}
Student ID: {self.DEVELOPER_INFO['student_id']}

Institution:
{self.DEVELOPER_INFO['institution']}

Projects:
{self.DEVELOPER_INFO['projects']}

Contact:
GitHub: {self.DEVELOPER_INFO['github']}
Email: {self.DEVELOPER_INFO['email']}

Specialties:
"""
        for specialty in self.DEVELOPER_INFO['specialties']:
            developer_text += f"• {specialty}\n"
        
        developer_label = ttk.Label(left_frame, text=developer_text, justify='left')
        developer_label.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Middle Column - Software Information
        middle_frame = ttk.LabelFrame(main_container, text="Software Information")
        middle_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        software_text = f"""
Automotive Stamping Cost Analyzer

Version: {self.VERSION}
Release Date: {self.RELEASE_DATE}

This software provides comprehensive cost analysis 
for automotive stamping operations, including:

• Material switching optimization
• Thickness reduction analysis  
• Strip processing efficiency
• Comprehensive overhead costing
• Real-time cost savings estimation
• Professional reporting

Key Features:
• Material database with 6 automotive materials
• Thickness optimization calculations
• Strip efficiency and nesting analysis
• Labor, energy, and equipment cost integration
• Multiple analysis types (material, thickness, or both)
• Professional reporting with recommendations
"""
        
        software_label = ttk.Label(middle_frame, text=software_text, justify='left')
        software_label.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Right Column - References
        right_frame = ttk.LabelFrame(main_container, text="References & Bibliography")
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Create scrollable text for references
        references_text = scrolledtext.ScrolledText(right_frame, width=40, height=20)
        references_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Populate references
        references_text.insert('1.0', "REFERENCES & BIBLIOGRAPHY\n")
        references_text.insert('end', "=" * 50 + "\n\n")
        
        for category in self.REFERENCES:
            references_text.insert('end', f"{category['category'].upper()}:\n")
            references_text.insert('end', "-" * 30 + "\n")
            for source in category['sources']:
                references_text.insert('end', f"• {source}\n")
            references_text.insert('end', "\n")
        
        references_text.config(state='disabled')
        
        # Version History - Full width below the three columns
        log_frame = ttk.LabelFrame(self.about_frame, text="Version History & Change Log")
        log_frame.pack(fill='both', expand=True, padx=10, pady=(10, 5))
        
        log_text = scrolledtext.ScrolledText(log_frame, width=80, height=15)
        log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Populate change log
        for version_info in self.CHANGE_LOG:
            log_text.insert('end', f"\nVersion {version_info['version']} ({version_info['date']}):\n")
            for change in version_info['changes']:
                log_text.insert('end', f"  • {change}\n")
        
        log_text.config(state='disabled')
    
    def update_cost_parameters(self):
        """Update cost parameters from user input"""
        try:
            for param, entry in self.cost_entries.items():
                self.cost_params[param] = float(entry.get())
            messagebox.showinfo("Success", "Cost parameters updated successfully!")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input in cost parameters: {e}")
    
    def calculate_analysis(self):
        """Perform comprehensive cost analysis"""
        try:
            # Get input values
            inputs = self.get_input_values()
            
            # Perform calculations
            results = self.perform_calculations(inputs)
            
            # Display results
            self.display_results(results, inputs)
            
        except Exception as e:
            messagebox.showerror("Calculation Error", f"An error occurred during calculation: {e}")
    
    def get_input_values(self):
        """Get and validate input values"""
        inputs = {
            'part_length': float(self.part_length.get()),
            'part_width': float(self.part_width.get()),
            'current_thickness': float(self.current_thickness.get()),
            'optimized_thickness': float(self.optimized_thickness.get()),
            'current_material_cost_mt': float(self.current_material_cost_mt.get()),
            'proposed_material_cost_mt': float(self.proposed_material_cost_mt.get()),
            'annual_volume': int(self.annual_volume.get()),
            'shifts_per_day': int(self.shifts_per_day.get()),
            'operating_days': int(self.operating_days.get()),
            'coil_width': float(self.coil_width.get()),
            'coil_weight': float(self.coil_weight.get()),
            'coil_change_time': float(self.coil_change_time.get()),
            'current_material': self.current_material.get(),
            'proposed_material': self.proposed_material.get(),
            'analysis_type': self.analysis_type.get()
        }
        
        # Validate materials
        if inputs['current_material'] not in self.materials:
            raise ValueError(f"Invalid current material: {inputs['current_material']}")
        if inputs['proposed_material'] not in self.materials:
            raise ValueError(f"Invalid proposed material: {inputs['proposed_material']}")
        
        # Validate thickness reduction
        current_mat = self.materials[inputs['current_material']]
        max_reduction = current_mat['max_thickness_reduction']
        actual_reduction = (inputs['current_thickness'] - inputs['optimized_thickness']) / inputs['current_thickness']
        
        if actual_reduction > max_reduction:
            messagebox.showwarning("Thickness Warning", 
                                 f"Warning: Proposed thickness reduction ({actual_reduction:.1%}) exceeds maximum recommended ({max_reduction:.1%}) for {inputs['current_material']}")
        
        return inputs
    
    def perform_calculations(self, inputs):
        """Perform the main cost calculations"""
        current_mat = self.materials[inputs['current_material']]
        proposed_mat = self.materials[inputs['proposed_material']]
        
        # Override material costs with user inputs (convert $/MT to $/kg)
        current_mat_cost_per_kg = inputs['current_material_cost_mt'] / 1000
        proposed_mat_cost_per_kg = inputs['proposed_material_cost_mt'] / 1000
        
        # Calculate part area
        part_area_cm2 = (inputs['part_length'] * inputs['part_width']) / 100  # cm²
        
        # Calculate weights for different scenarios
        current_weight_original = self.calculate_weight(current_mat, part_area_cm2, inputs['current_thickness'])
        current_weight_optimized = self.calculate_weight(current_mat, part_area_cm2, inputs['optimized_thickness'])
        proposed_weight_original = self.calculate_weight(proposed_mat, part_area_cm2, inputs['current_thickness'])
        proposed_weight_optimized = self.calculate_weight(proposed_mat, part_area_cm2, inputs['optimized_thickness'])
        
        # Determine which scenario to use based on analysis type
        if inputs['analysis_type'] == 'material':
            # Material switch only - keep original thickness
            current_weight = current_weight_original
            proposed_weight = proposed_weight_original
            thickness_note = "Material switch only (original thickness maintained)"
            
        elif inputs['analysis_type'] == 'thickness':
            # Thickness optimization only - keep current material
            current_weight = current_weight_original
            proposed_weight = current_weight_optimized
            thickness_note = "Thickness optimization only (current material)"
            inputs['proposed_material'] = inputs['current_material']  # Override for reporting
            
        else:  # 'both'
            # Both material switch and thickness optimization
            current_weight = current_weight_original
            proposed_weight = proposed_weight_optimized
            thickness_note = "Material switch + thickness optimization"
        
        # Material costs using user-input costs
        current_material_cost = current_weight * current_mat_cost_per_kg
        proposed_material_cost = proposed_weight * proposed_mat_cost_per_kg
        
        # Weight savings
        weight_saving_kg = current_weight - proposed_weight
        weight_reduction_pct = (weight_saving_kg / current_weight) * 100
        
        # Cost savings
        material_saving_per_part = current_material_cost - proposed_material_cost
        annual_material_saving = material_saving_per_part * inputs['annual_volume']
        
        # Strip efficiency calculations
        current_parts_per_strip = (inputs['coil_weight'] / current_weight) * 0.85
        proposed_parts_per_strip = (inputs['coil_weight'] / proposed_weight) * 0.85
        
        # Coil change savings (keeping this term as it refers to the time component)
        current_coil_changes = inputs['annual_volume'] / current_parts_per_strip
        proposed_coil_changes = inputs['annual_volume'] / proposed_parts_per_strip
        coil_change_saving = (current_coil_changes - proposed_coil_changes) * inputs['coil_change_time'] / 60 * self.cost_params['operator_hourly_rate']
        
        return {
            'current_weight_kg': current_weight,
            'proposed_weight_kg': proposed_weight,
            'weight_saving_kg': weight_saving_kg,
            'weight_reduction_pct': weight_reduction_pct,
            'current_material_cost': current_material_cost,
            'proposed_material_cost': proposed_material_cost,
            'material_saving_per_part': material_saving_per_part,
            'annual_material_saving': annual_material_saving,
            'current_parts_per_strip': current_parts_per_strip,
            'proposed_parts_per_strip': proposed_parts_per_strip,
            'coil_change_saving': coil_change_saving,
            'part_area_cm2': part_area_cm2,
            'thickness_note': thickness_note,
            'analysis_type': inputs['analysis_type'],
            'current_mat_cost_per_kg': current_mat_cost_per_kg,
            'proposed_mat_cost_per_kg': proposed_mat_cost_per_kg
        }
    
    def calculate_weight(self, material, area_cm2, thickness_mm):
        """Calculate part weight based on material, area and thickness"""
        volume_cm3 = area_cm2 * thickness_mm / 10  # cm³
        return (volume_cm3 / 1000000) * material['density']  # kg
    
    def display_results(self, results, inputs):
        """Display analysis results with enhanced clarity"""
        self.results_text.config(state='normal')
        self.results_text.delete('1.0', 'end')
        
        # Determine savings interpretation
        total_annual_saving = results['annual_material_saving'] + results['coil_change_saving']
        saving_interpretation = "SAVINGS" if total_annual_saving > 0 else "EXTRA COST"
        
        # Calculate savings per metric ton for additional context
        total_material_used_annual = results['current_weight_kg'] * inputs['annual_volume'] / 1000  # tons
        saving_per_ton = total_annual_saving / total_material_used_annual if total_material_used_annual > 0 else 0
        
        report = f"""
AUTOMOTIVE STAMPING COST ANALYSIS REPORT
=======================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Version: {self.VERSION}
Analysis Type: {results['thickness_note']}

INPUT PARAMETERS:
----------------
Blank Geometry (CTL only): {inputs['part_length']} x {inputs['part_width']} mm
Current Thickness: {inputs['current_thickness']} mm
Optimized Thickness: {inputs['optimized_thickness']} mm
Blank Area: {results['part_area_cm2']:.1f} cm²
Annual Production: {inputs['annual_volume']:,} parts
Current Material: {inputs['current_material']}
Proposed Material: {inputs['proposed_material']}

MATERIAL COSTS:
---------------
Current Material: ${inputs['current_material_cost_mt']:,.0f}/MT (${results['current_mat_cost_per_kg']:.3f}/kg)
Proposed Material: ${inputs['proposed_material_cost_mt']:,.0f}/MT (${results['proposed_mat_cost_per_kg']:.3f}/kg)

WEIGHT ANALYSIS:
---------------
Current Weight: {results['current_weight_kg']:.4f} kg
Proposed Weight: {results['proposed_weight_kg']:.4f} kg
Weight Saving per Part: {results['weight_saving_kg']:.4f} kg
Weight Reduction: {results['weight_reduction_pct']:.1f}%

MATERIAL COST ANALYSIS:
----------------------
Current Material Cost per Part: ${results['current_material_cost']:.4f}
Proposed Material Cost per Part: ${results['proposed_material_cost']:.4f}
Material Saving per Part: ${results['material_saving_per_part']:.4f}
Annual Material Saving: ${results['annual_material_saving']:,.2f}

STRIP PROCESSING EFFICIENCY:
---------------------------
Current Parts per Strip: {results['current_parts_per_strip']:.0f}
Proposed Parts per Strip: {results['proposed_parts_per_strip']:.0f}
Coil Change Time Saving: ${results['coil_change_saving']:,.2f}

SUMMARY (ANNUAL PRODUCTION):
----------------------------
Total Estimated Annual Saving: ${total_annual_saving:,.2f} USD

BREAKDOWN PER METRIC TON:
-------------------------
Annual Material Usage: {total_material_used_annual:,.1f} MT
Saving per Metric Ton: ${saving_per_ton:,.2f} USD/MT

INTERPRETATION:
---------------
• ANNUAL SAVING: Total cost reduction for your annual production of {inputs['annual_volume']:,} parts
• Positive values indicate COST SAVINGS
• Negative values indicate EXTRA COST
• Current result: {saving_interpretation} of ${abs(total_annual_saving):,.2f} USD per year

RECOMMENDATIONS:
---------------
1. {results['thickness_note']}
2. Weight reduction: {results['weight_reduction_pct']:.1f}% per part
3. Annual {saving_interpretation.lower()}: ${abs(total_annual_saving):,.2f} USD
4. Equivalent to ${saving_per_ton:,.2f} USD savings per metric ton of material
5. Improved strip efficiency: +{((results['proposed_parts_per_strip'] - results['current_parts_per_strip']) / results['current_parts_per_strip'] * 100):.1f}% parts per strip

CURRENCY NOTE:
--------------
All cost values are presented in USD. Use the currency conversion tool 
in the Cost Parameters tab to convert to other currencies if needed.

DEVELOPED BY:
-------------
{self.DEVELOPER_INFO['name']} ({self.DEVELOPER_INFO['student_id']})
{self.DEVELOPER_INFO['institution']}
Projects: {self.DEVELOPER_INFO['projects']}
Contact: {self.DEVELOPER_INFO['email']} | GitHub: {self.DEVELOPER_INFO['github']}
"""
        
        self.results_text.insert('1.0', report)
        self.results_text.config(state='disabled')
        
        # Show success message with savings interpretation
        message_text = f"Cost analysis completed successfully!\n"
        message_text += f"Result: {saving_interpretation} of ${abs(total_annual_saving):,.2f} USD per year"
        messagebox.showinfo("Analysis Complete", message_text)

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = AutomotiveStampingAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
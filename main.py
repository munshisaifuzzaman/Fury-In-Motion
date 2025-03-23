import streamlit as st

# ✅ import the full module, not individual variables
import components.controls as controls
from components.observers import setup_observers
from utils.data_loader import load_tornado_data, validate_original_data

# ✅ Load and validate data
tornado_data = load_tornado_data()
validate_original_data(tornado_data)

# ✅ Inject data into controls module so observers.py can use it
controls.tornado_data = tornado_data

# ✅ Setup interactive UI and callbacks
setup_observers()

# ✅ Render map and outputs
controls.output
controls.map_output
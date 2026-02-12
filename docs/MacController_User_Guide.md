# 🖥️ HardCard MacController User Guide

**Complete guide to automating macOS with enterprise-grade security and reliability**

---

## 📖 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation & Setup](#installation--setup)
3. [Basic Operations](#basic-operations)
4. [Advanced Features](#advanced-features)
5. [VetSorcery Integration](#vetsorcery-integration)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)

---

## 🚀 Quick Start

Get up and running with MacController in under 5 minutes:

### 1. Basic Setup

```python
from hardcard.macos_integration import MacController

# Initialize the controller
controller = MacController()

# Take a screenshot
result = await controller.take_screenshot()
if result.success:
    print(f"Screenshot saved: {result.data.path}")
else:
    print(f"Error: {result.error.message}")
```

### 2. Simple Automation

```python
# Launch an application and wait for it to be ready
launch_result = await controller.launch_application("Calculator", wait_for_launch=True)

if launch_result.success:
    # Click at coordinates and type
    await controller.click_coordinates(100, 200)
    await controller.type_text("2+2=")
    await controller.press_key("return")
```

### 3. Secure Credential Management

```python
# Store credentials securely in macOS Keychain
controller.store_avimark_credentials(
    username="your_username", 
    password="your_password",
    credential_key="clinic_main"
)

# Use stored credentials
login_result = await controller.automate_avimark_login("clinic_main")
```

---

## 🛠️ Installation & Setup

### Prerequisites

- **macOS 10.15+** (Catalina or later)
- **Python 3.8+**
- **Accessibility permissions** for automation
- **cliclick utility** for mouse/keyboard control

### Installation

```bash
# Install HardCard MacController
pip install hardcard-macos

# Install cliclick (required for mouse/keyboard automation)
brew install cliclick

# Or download from: https://github.com/BlueM/cliclick
```

### Accessibility Permissions

**CRITICAL**: macOS requires explicit permission for automation:

1. **System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Accessibility** from the left sidebar
3. Click the **lock** icon and enter your password
4. Click **+** and add your Python application or Terminal
5. Ensure the checkbox is **checked**

```python
# Test permissions
from hardcard.macos_integration import MacController

controller = MacController()
system_info = await controller.get_system_info()

if system_info.success:
    print("✅ Permissions are working!")
    print(f"macOS Version: {system_info.data.macos_version}")
else:
    print("❌ Check your accessibility permissions")
    print(f"Error: {system_info.error.message}")
```

---

## 🎯 Basic Operations

### Mouse Control

```python
# Click at specific coordinates
click_result = await controller.click_coordinates(500, 300)
print(f"Click successful: {click_result.success}")

# Multiple clicks with timing control
multi_click = await controller.multi_click(
    coordinates=(500, 300),
    clicks=3,
    interval=0.2  # 200ms between clicks
)

# Right-click with context menu detection
right_click = await controller.right_click(
    coordinates=(500, 300),
    wait_for_menu=True,
    menu_timeout=2.0
)

# Drag and drop operations
drag_result = await controller.drag_and_drop(
    start=(100, 100),
    end=(200, 200),
    duration=1.5,    # 1.5 seconds
    steps=20         # Smooth movement
)

# Mouse movement and position
await controller.move_mouse(400, 300)
position = await controller.get_mouse_position()
print(f"Mouse at: ({position.data.x}, {position.data.y})")
```

### Keyboard Input

```python
# Type text with configurable delay
type_result = await controller.type_text(
    "Hello, World!",
    delay_ms=50  # 50ms between characters
)

# Type with formatting (bold, italic, underline)
formatted_text = await controller.type_with_formatting(
    "Important Notice",
    formatting=["bold", "underline"],
    delay_ms=30
)

# Press individual keys
await controller.press_key("return")
await controller.press_key("tab")
await controller.press_key("escape")

# Key combinations (shortcuts)
await controller.press_key_combination(["cmd", "c"])      # Copy
await controller.press_key_combination(["cmd", "shift", "n"])  # New window
await controller.press_key_combination(["option", "tab"])      # App switcher
```

### Screen Operations

```python
# Take full screenshot
screenshot = await controller.take_screenshot()
if screenshot.success:
    print(f"Screenshot: {screenshot.data.path}")
    print(f"Size: {screenshot.data.size_bytes} bytes")

# Screenshot specific region
region_screenshot = await controller.take_screenshot(
    region=(100, 100, 400, 300),  # x, y, width, height
    save_path="/tmp/my_screenshot.png"
)

# Get screen dimensions
screen_size = await controller.get_screen_size()
if screen_size.success:
    print(f"Screen: {screen_size.data.width}x{screen_size.data.height}")

# Advanced scrolling
scroll_result = await controller.scroll(
    direction="down",
    amount=5,                    # 5 scroll units
    coordinates=(500, 400),      # Scroll at this location
    horizontal=False             # Vertical scrolling
)
```

---

## 🚁 Advanced Features

### Intelligent State Detection

```python
# Wait for specific text to appear on screen
text_found = await controller.wait_for_text_on_screen(
    text="Login Successful",
    timeout=30  # Wait up to 30 seconds
)

if text_found.success:
    print(f"Text found at: {text_found.data.coordinates}")
    print(f"Detection method: {text_found.data.detection_method}")

# Wait for UI elements with complex descriptors
element_found = await controller.wait_for_element(
    element_descriptor={
        "text": "Submit",
        "type": "button",
        "app": "Safari"
    },
    timeout=15
)

# Smart click - wait for text, then click it
smart_click = await controller.smart_wait_and_click(
    text_to_find="Continue",
    timeout=10,
    click_offset=(0, -5)  # Click slightly above the text
)
```

### Application Management

```python
# Launch applications with readiness verification
app_result = await controller.launch_application(
    "Avimark",
    wait_for_launch=True
)

if app_result.success:
    print(f"Application launched: {app_result.data.app_name}")
    print(f"Process ID: {app_result.data.process_id}")

# Check application status
status = await controller.is_application_running("Avimark")
if status.success and status.data.running:
    print("Avimark is running")

# Focus and manage windows
await controller.focus_window("Avimark")

# Wait for application to be fully ready
ready = await controller.wait_for_application_ready(
    "Avimark",
    timeout=30
)

# Graceful application shutdown
quit_result = await controller.quit_application("Avimark")
```

### System Information & Monitoring

```python
# Comprehensive system information
sys_info = await controller.get_system_info()
if sys_info.success:
    info = sys_info.data
    print(f"macOS Version: {info.macos_version}")
    print(f"Hardware Model: {info.hardware['model']}")
    print(f"Processor: {info.hardware['processor']}")
    print(f"Memory: {info.hardware['memory']}")
    
# Real-time performance monitoring
async def monitor_system():
    while True:
        info = await controller.get_system_info()
        if info.success:
            print(f"Memory: {info.data.memory_stats}")
            print(f"Disk: {info.data.disk_info}")
        await asyncio.sleep(60)  # Check every minute
```

---

## 🏥 VetSorcery Integration

MacController provides specialized methods for veterinary practice management:

### Secure Login Automation

```python
# Store clinic credentials securely
store_result = controller.store_avimark_credentials(
    username="clinic_user",
    password="secure_password",
    credential_key="main_clinic"
)

if store_result["success"]:
    print("Credentials stored securely in macOS Keychain")

# Automated login with state detection
login_result = await controller.automate_avimark_login("main_clinic")

if login_result.success:
    print("Successfully logged into Avimark")
    print("Main window is ready for automation")
else:
    print(f"Login failed: {login_result.error.message}")
    # Check credentials or application state
```

### Appointment Management

```python
# Automate appointment booking
client_info = {
    "client_id": "12345",
    "pet_name": "Buddy",
    "appointment_time": "2025-01-15 14:30",
    "services": ["Annual Exam", "Vaccinations"],
    "doctor": "Dr. Smith"
}

booking_result = await controller.automate_appointment_booking(client_info)

if booking_result.success:
    print("Appointment booked successfully")
else:
    print(f"Booking failed: {booking_result.error.message}")
```

### Multi-Clinic Management

```python
# Manage multiple clinic credentials
clinics = [
    {"name": "Main Clinic", "key": "main_clinic"},
    {"name": "Branch Office", "key": "branch_clinic"},
    {"name": "Emergency Center", "key": "emergency_clinic"}
]

for clinic in clinics:
    # Store credentials for each clinic
    controller.store_avimark_credentials(
        username=f"user_{clinic['name']}",
        password="clinic_password",
        credential_key=clinic['key']
    )

# Get list of stored credentials
stored_keys = controller.get_stored_credential_keys()
if stored_keys["success"]:
    print(f"Available clinics: {stored_keys['credential_keys']}")

# Login to specific clinic
await controller.automate_avimark_login("main_clinic")
```

---

## ⚠️ Error Handling

MacController uses a comprehensive error handling system with specific exception types:

### Understanding Response Format

```python
# All operations return ControllerResponse objects
result = await controller.click_coordinates(100, 200)

# Check success
if result.success:
    # Access successful data
    click_data = result.data
    print(f"Clicked at: {click_data.coordinates}")
    print(f"Execution time: {result.metadata.execution_time}s")
else:
    # Handle errors
    error = result.error
    print(f"Error Code: {error.code}")
    print(f"Message: {error.message}")
    print(f"Details: {error.details}")
    
    # Get timestamp for logging
    print(f"Error occurred at: {error.timestamp}")
```

### Specific Error Types

```python
from hardcard.macos_integration.exceptions import (
    ApplicationNotFoundError,
    PermissionError,
    TimeoutError,
    ValidationError,
    CredentialNotFoundError
)

try:
    result = await controller.launch_application("NonExistentApp")
    if not result.success:
        if result.error.code == "APP_NOT_FOUND":
            print("Application not found - check the app name")
        elif result.error.code == "PERMISSION_DENIED":
            print("Check accessibility permissions")
        elif result.error.code == "OPERATION_TIMEOUT":
            print("Application took too long to launch")

except Exception as e:
    print(f"Unexpected error: {e}")
```

### Retry Logic and Recovery

```python
import asyncio

async def robust_click_with_retry(controller, x, y, max_retries=3):
    """Example of robust clicking with retry logic"""
    
    for attempt in range(max_retries):
        try:
            result = await controller.click_coordinates(x, y)
            
            if result.success:
                return result
            
            # Check if error is recoverable
            if result.error.code in ["PERMISSION_DENIED", "VALIDATION_ERROR"]:
                # Non-recoverable errors
                return result
            
            # Recoverable error - wait and retry
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            await asyncio.sleep(2 ** attempt)
    
    return create_error_response("Max retries exceeded")

# Usage
result = await robust_click_with_retry(controller, 500, 300)
```

---

## 💡 Best Practices

### 1. Always Check Permissions First

```python
async def check_system_readiness():
    """Verify system is ready for automation"""
    
    # Test basic functionality
    system_info = await controller.get_system_info()
    if not system_info.success:
        print("❌ System access failed - check permissions")
        return False
    
    # Test mouse control
    mouse_pos = await controller.get_mouse_position()
    if not mouse_pos.success:
        print("❌ Mouse control failed - check accessibility")
        return False
    
    # Test screenshot capability
    screenshot = await controller.take_screenshot()
    if not screenshot.success:
        print("❌ Screenshot failed - check screen recording permissions")
        return False
    
    print("✅ System ready for automation")
    return True
```

### 2. Use State Detection Instead of Fixed Delays

```python
# ❌ Bad - using fixed delays
await controller.click_coordinates(100, 200)
await asyncio.sleep(3)  # Hope the dialog appears
await controller.type_text("username")

# ✅ Good - using state detection
await controller.click_coordinates(100, 200)
login_dialog = await controller.wait_for_text_on_screen("Username:", timeout=10)
if login_dialog.success:
    await controller.type_text("username")
```

### 3. Implement Proper Error Handling

```python
async def safe_automation_sequence():
    """Example of safe automation with proper error handling"""
    
    try:
        # Launch application
        app_result = await controller.launch_application("Avimark")
        if not app_result.success:
            raise Exception(f"Failed to launch: {app_result.error.message}")
        
        # Wait for application to be ready
        ready_result = await controller.wait_for_application_ready("Avimark", timeout=30)
        if not ready_result.success:
            await controller.quit_application("Avimark")  # Cleanup
            raise Exception("Application not ready")
        
        # Perform automation tasks
        login_result = await controller.automate_avimark_login("main_clinic")
        if not login_result.success:
            raise Exception(f"Login failed: {login_result.error.message}")
        
        return {"success": True, "message": "Automation completed"}
        
    except Exception as e:
        # Cleanup on error
        await controller.quit_application("Avimark")
        return {"success": False, "error": str(e)}
```

### 4. Use Secure Credential Management

```python
# ✅ Good - secure credential storage
def setup_clinic_credentials():
    """Setup credentials securely"""
    
    # Store in macOS Keychain
    result = controller.store_avimark_credentials(
        username=input("Enter username: "),
        password=getpass.getpass("Enter password: "),
        credential_key="primary_clinic"
    )
    
    if result["success"]:
        print("Credentials stored securely")
    else:
        print(f"Storage failed: {result['error']}")

# ❌ Bad - hardcoded credentials
# username = "hardcoded_user"  # Never do this!
# password = "hardcoded_pass"  # Security risk!
```

### 5. Log Operations for Audit Trail

```python
# MacController automatically logs operations for HIPAA compliance
# But you can add your own logging for business logic

import logging

logger = logging.getLogger("vet_automation")

async def log_patient_interaction(patient_id, action):
    """Log patient-related automation for audit trail"""
    
    logger.info(f"Patient {patient_id}: Starting {action}")
    
    try:
        # Perform automation
        result = await perform_automation_action(action)
        
        if result.success:
            logger.info(f"Patient {patient_id}: {action} completed successfully")
        else:
            logger.error(f"Patient {patient_id}: {action} failed - {result.error.message}")
        
        return result
        
    except Exception as e:
        logger.error(f"Patient {patient_id}: {action} exception - {str(e)}")
        raise
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. **Permission Denied Errors**

```
Error: PERMISSION_DENIED - Insufficient permissions for operation
```

**Solution:**
- Check **System Preferences** → **Security & Privacy** → **Accessibility**
- Ensure your Python app/Terminal is listed and enabled
- Try removing and re-adding the application

#### 2. **Application Not Found**

```
Error: APP_NOT_FOUND - Application 'Avimark' could not be found
```

**Solution:**
- Verify application name exactly (case-sensitive)
- Use full application path if needed
- Check if application is installed

```python
# Try different name variations
app_names_to_try = ["Avimark", "Avimark.app", "Avimark Professional"]
for name in app_names_to_try:
    result = await controller.launch_application(name)
    if result.success:
        print(f"Found application: {name}")
        break
```

#### 3. **Element Detection Timeouts**

```
Error: ELEMENT_NOT_FOUND - Element not found after timeout
```

**Solution:**
- Increase timeout value
- Verify text/element actually appears
- Use different detection methods
- Take screenshot to debug

```python
# Debug element detection
screenshot = await controller.take_screenshot()
print(f"Debug screenshot: {screenshot.data.path}")

# Try longer timeout
result = await controller.wait_for_text_on_screen("Login", timeout=60)
```

#### 4. **Credential Not Found**

```
Error: CREDENTIAL_NOT_FOUND - Credentials not found for key: clinic_main
```

**Solution:**
- Verify credential key spelling
- Re-store credentials if needed
- Check available keys

```python
# List available credential keys
keys = controller.get_stored_credential_keys()
print(f"Available keys: {keys['credential_keys']}")

# Re-store if needed
controller.store_avimark_credentials(
    username="your_username",
    password="your_password", 
    credential_key="clinic_main"
)
```

#### 5. **Screen Recording Permissions (macOS Catalina+)**

```
Error: SCREENSHOT_FAILED - Screen recording permission denied
```

**Solution:**
- **System Preferences** → **Security & Privacy** → **Privacy** → **Screen Recording**
- Add your Python application or Terminal
- Restart your Python script after granting permission

### Debug Mode

```python
# Enable detailed logging for debugging
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mac_controller")

# Use debug mode with extra information
controller = MacController()
controller.logger.setLevel(logging.DEBUG)

# All operations will now show detailed debug information
result = await controller.click_coordinates(100, 200)
```

### Performance Optimization

```python
# For high-frequency operations, reduce delays
await controller.type_text("fast text", delay_ms=10)  # Faster typing

# Cache screen size for repeated use
screen_size = await controller.get_screen_size()
if screen_size.success:
    width, height = screen_size.data.width, screen_size.data.height
    # Use cached values instead of repeated calls

# Use batch operations when possible
actions = [
    controller.click_coordinates(100, 100),
    controller.type_text("hello"),
    controller.press_key("return")
]
results = await asyncio.gather(*actions)
```

---

## 📚 API Reference

### Core Classes

#### `MacController`
Main controller class for macOS automation.

**Constructor:**
```python
MacController()
```

**Properties:**
- `session_id: str` - Unique session identifier
- `allowed_commands: set` - Set of allowed shell commands
- `max_command_length: int` - Maximum command length (default: 1000)

### Response Types

#### `ControllerResponse[T]`
Standardized response format for all operations.

**Properties:**
- `success: bool` - Operation success status
- `data: T` - Response data (when successful)
- `error: ErrorInfo` - Error information (when failed)
- `metadata: ResponseMetadata` - Operation metadata

#### `Point`
Screen coordinate representation.

**Properties:**
- `x: int` - X coordinate
- `y: int` - Y coordinate

**Methods:**
- `to_tuple() -> Tuple[int, int]` - Convert to tuple format

#### `ScreenRegion`
Screen region definition.

**Properties:**
- `x, y, width, height: int` - Region dimensions
- `top_left: Point` - Top-left corner
- `bottom_right: Point` - Bottom-right corner
- `center: Point` - Center point

### Error Types

#### Exception Hierarchy
```
MacControllerError
├── ApplicationError
│   ├── ApplicationNotFoundError
│   └── ApplicationNotResponsiveError
├── PermissionError
├── TimeoutError
├── ValidationError
├── ScreenError
│   ├── ElementNotFoundError
│   └── ScreenshotError
├── CommandExecutionError
├── SecurityError
│   ├── CommandNotAllowedError
│   └── DangerousPatternError
├── CredentialError
│   ├── CredentialNotFoundError
│   └── CredentialStorageError
└── StateDetectionError
    ├── OCRError
    └── TemplateMatchError
```

### Method Categories

#### **Mouse Operations**
- `click_coordinates(x, y, clicks=1)` - Basic clicking
- `multi_click(coordinates, clicks, interval)` - Multiple clicks with timing
- `right_click(coordinates, wait_for_menu, menu_timeout)` - Context menu clicking
- `drag_and_drop(start, end, duration, steps)` - Drag and drop operations
- `move_mouse(x, y)` - Cursor movement
- `get_mouse_position()` - Current cursor position

#### **Keyboard Operations**
- `type_text(text, delay_ms)` - Basic text input
- `type_with_formatting(text, formatting, delay_ms)` - Formatted text input
- `press_key(key)` - Single key press
- `press_key_combination(keys)` - Key combinations/shortcuts

#### **Screen Operations**
- `take_screenshot(region, save_path)` - Screen capture
- `get_screen_size()` - Display dimensions
- `scroll(direction, amount, coordinates, horizontal)` - Scrolling

#### **Application Management**
- `launch_application(app_name, wait_for_launch)` - Launch apps
- `quit_application(app_name)` - Quit apps
- `is_application_running(app_name)` - Check app status
- `focus_window(app_name)` - Window focusing
- `wait_for_application_ready(app_name, timeout)` - Wait for app readiness

#### **State Detection**
- `wait_for_element(element_descriptor, timeout)` - Wait for UI elements
- `wait_for_text_on_screen(text, timeout)` - Wait for text
- `smart_wait_and_click(text_to_find, timeout, click_offset)` - Intelligent clicking

#### **VetSorcery Integration**
- `automate_avimark_login(credential_key)` - Automated login
- `automate_appointment_booking(client_info)` - Appointment automation
- `store_avimark_credentials(username, password, credential_key)` - Credential storage
- `get_stored_credential_keys()` - List stored credentials

#### **System Information**
- `get_system_info()` - Comprehensive system data
- `execute_command(command, timeout)` - Secure command execution

---

## 🎓 Advanced Examples

### Complete Workflow Example

```python
async def complete_patient_checkin_workflow():
    """Complete example of patient check-in automation"""
    
    controller = MacController()
    
    try:
        # 1. Launch and login to Avimark
        print("🚀 Launching Avimark...")
        app_result = await controller.launch_application("Avimark", wait_for_launch=True)
        
        if not app_result.success:
            raise Exception(f"Failed to launch Avimark: {app_result.error.message}")
        
        # 2. Automated login with stored credentials
        print("🔐 Logging in...")
        login_result = await controller.automate_avimark_login("main_clinic")
        
        if not login_result.success:
            raise Exception(f"Login failed: {login_result.error.message}")
        
        # 3. Navigate to patient check-in
        print("📋 Navigating to check-in...")
        
        # Wait for main menu and click Appointments
        menu_found = await controller.smart_wait_and_click(
            text_to_find="Appointments",
            timeout=10
        )
        
        if not menu_found.success:
            raise Exception("Could not find Appointments menu")
        
        # 4. Search for patient
        print("🔍 Searching for patient...")
        
        # Wait for search field
        search_found = await controller.wait_for_text_on_screen("Search:", timeout=10)
        if search_found.success:
            # Click in search field and enter patient name
            await controller.click_coordinates(*search_found.data.coordinates)
            await controller.type_text("Smith, John")
            await controller.press_key("return")
        
        # 5. Select patient and check in
        print("✅ Checking in patient...")
        
        # Wait for patient to appear and double-click
        patient_found = await controller.wait_for_text_on_screen("Smith, John", timeout=15)
        if patient_found.success:
            # Double-click to select patient
            await controller.multi_click(
                coordinates=patient_found.data.coordinates,
                clicks=2,
                interval=0.3
            )
            
            # Click check-in button
            checkin_button = await controller.smart_wait_and_click(
                text_to_find="Check In",
                timeout=5
            )
            
            if checkin_button.success:
                print("🎉 Patient check-in completed successfully!")
                return {"success": True, "message": "Check-in completed"}
            else:
                raise Exception("Could not find Check In button")
        else:
            raise Exception("Patient not found in search results")
    
    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")
        
        # Take screenshot for debugging
        debug_screenshot = await controller.take_screenshot()
        if debug_screenshot.success:
            print(f"Debug screenshot saved: {debug_screenshot.data.path}")
        
        return {"success": False, "error": str(e)}

# Run the workflow
result = await complete_patient_checkin_workflow()
```

### Multi-Application Workflow

```python
async def multi_app_workflow():
    """Example using multiple applications"""
    
    controller = MacController()
    
    # 1. Get patient data from Excel
    await controller.launch_application("Microsoft Excel")
    
    excel_ready = await controller.wait_for_application_ready("Microsoft Excel", timeout=30)
    if excel_ready.success:
        # Select and copy patient data
        await controller.press_key_combination(["cmd", "a"])  # Select all
        await controller.press_key_combination(["cmd", "c"])  # Copy
    
    # 2. Switch to Avimark and enter data
    await controller.focus_window("Avimark")
    
    avimark_ready = await controller.wait_for_application_ready("Avimark", timeout=10)
    if avimark_ready.success:
        # Paste patient data
        await controller.press_key_combination(["cmd", "v"])
    
    # 3. Send confirmation email
    await controller.launch_application("Mail")
    
    mail_ready = await controller.wait_for_application_ready("Mail", timeout=20)
    if mail_ready.success:
        # Compose email
        await controller.press_key_combination(["cmd", "n"])  # New email
        
        # Wait for compose window
        compose_found = await controller.wait_for_text_on_screen("To:", timeout=10)
        if compose_found.success:
            await controller.type_text("patient@example.com")
            await controller.press_key("tab")  # Move to subject
            await controller.type_text("Appointment Confirmation")
            await controller.press_key("tab")  # Move to body
            await controller.type_text("Your appointment has been confirmed.")
            
            # Send email
            await controller.press_key_combination(["cmd", "shift", "d"])
    
    print("Multi-application workflow completed")
```

---

## 🏆 Conclusion

The HardCard MacController provides enterprise-grade macOS automation with:

- **🔒 Security-First Design** - Built-in security controls and audit trails
- **🎯 Intelligent Automation** - State detection instead of fixed delays  
- **📱 Easy Integration** - Simple API with comprehensive error handling
- **🏥 VetSorcery Ready** - Specialized veterinary workflow automation
- **📚 Complete Documentation** - Comprehensive guides and examples

### Next Steps

1. **Start Simple** - Begin with basic operations and build up
2. **Test Permissions** - Ensure all accessibility permissions are granted
3. **Use State Detection** - Implement robust automation with intelligent waiting
4. **Handle Errors** - Implement proper error handling and recovery
5. **Monitor Performance** - Use logging and monitoring for production use

### Support and Resources

- **Documentation**: `/docs/` directory for detailed guides
- **Examples**: `/examples/` directory for sample code
- **Troubleshooting**: This guide's troubleshooting section
- **Security**: Security audit reports in project root

**Happy Automating! 🚀**

---

*This guide covers HardCard MacController v2.0+ with enhanced security and state detection capabilities.*
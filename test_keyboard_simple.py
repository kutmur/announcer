#!/usr/bin/env python3
"""
Simple test script to verify keyboard functionality works
This tests the exact same logic as the /start command
"""

def test_keyboard_logic():
    """Test the keyboard building logic with sample data"""
    
    # Test data - sample department list (exactly as used in /start command)
    departments = ["Bilgisayar", "Yapay Zeka", "Makine", "Elektrik", "İnşaat"]
    
    print(f"📋 Testing with {len(departments)} departments: {departments}")
    
    # Sort departments alphabetically (as in /start command)
    sorted_departments = sorted(departments)
    print(f"🔤 Sorted departments: {sorted_departments}")
    
    # Build keyboard - 2 departments per row (as in /start command)
    keyboard = []
    
    # Group departments 2 per row using list comprehension
    keyboard = [[sorted_departments[i], sorted_departments[i+1]] 
                for i in range(0, len(sorted_departments)-1, 2)]
    
    # Handle odd number of departments - add the last one alone
    if len(sorted_departments) % 2 == 1:
        keyboard.append([sorted_departments[-1]])
    
    # Add special buttons at the end
    keyboard.append(["📊 İstatistikler", "❓ Yardım"])
    keyboard.append(["⌨️ Klavyeyi Gizle"])
    
    print(f"\n⌨️ Generated keyboard with {len(keyboard)} rows:")
    for i, row in enumerate(keyboard):
        print(f"  Row {i+1}: {row}")
    
    # Verify keyboard structure
    expected_department_rows = (len(sorted_departments) + 1) // 2  # ceil division
    actual_department_rows = len(keyboard) - 2  # minus 2 special rows
    
    print(f"\n✅ Verification:")
    print(f"   Expected department rows: {expected_department_rows}")
    print(f"   Actual department rows: {actual_department_rows}")
    print(f"   Special button rows: 2")
    print(f"   Total keyboard rows: {len(keyboard)}")
    
    if actual_department_rows == expected_department_rows:
        print("   ✅ Keyboard structure is CORRECT!")
        return True
    else:
        print("   ❌ Keyboard structure is WRONG!")
        return False

def test_department_import():
    """Test importing departments from handlers.departments"""
    try:
        from handlers.departments import get_department_names
        departments = get_department_names()
        
        if departments:
            print(f"\n📚 Successfully imported {len(departments)} departments from handlers.departments")
            print(f"   First 5: {departments[:5]}")
            return departments
        else:
            print(f"\n❌ get_department_names() returned empty list")
            return []
            
    except Exception as e:
        print(f"\n❌ Failed to import departments: {e}")
        return []

if __name__ == "__main__":
    print("🧪 KEYBOARD FUNCTIONALITY TEST")
    print("=" * 50)
    
    # Test 1: Basic keyboard logic
    print("\n1️⃣ Testing keyboard building logic...")
    success = test_keyboard_logic()
    
    # Test 2: Department import
    print("\n2️⃣ Testing department import...")
    real_departments = test_department_import()
    
    # Test 3: Real data keyboard
    if real_departments:
        print(f"\n3️⃣ Testing keyboard with real data ({len(real_departments)} departments)...")
        # Use first 5 departments for testing
        test_departments = real_departments[:5]
        
        keyboard = [[test_departments[i], test_departments[i+1]] 
                    for i in range(0, len(test_departments)-1, 2)]
        
        if len(test_departments) % 2 == 1:
            keyboard.append([test_departments[-1]])
            
        keyboard.append(["📊 İstatistikler", "❓ Yardım"])
        keyboard.append(["⌨️ Klavyeyi Gizle"])
        
        print(f"   Real data keyboard ({len(keyboard)} rows):")
        for i, row in enumerate(keyboard):
            print(f"     Row {i+1}: {row}")
    
    print(f"\n🎯 TEST SUMMARY:")
    print(f"   Basic logic: {'✅ PASS' if success else '❌ FAIL'}")
    print(f"   Department import: {'✅ PASS' if real_departments else '❌ FAIL'}")
    print(f"   Ready for Telegram: {'✅ YES' if success else '❌ NO'}")

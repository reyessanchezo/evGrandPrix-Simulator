def analyze_rpm_from_log(log_file_path):
    rpms = []
    
    try:
        with open(log_file_path, 'r') as file:
            for line in file:
                # Split the line by comma and space
                parts = line.split(', ')
                
                # Find the RPM value
                # Looking for the part that starts with "RPM: "
                for part in parts:
                    if part.startswith('RPM: '):
                        rpm = float(part.split(': ')[1])
                        rpms.append(rpm)
        
        if not rpms:
            return None, None
            
        avg_rpm = sum(rpms) / len(rpms)
        max_rpm = max(rpms)
        
        return avg_rpm, max_rpm
        
    except FileNotFoundError:
        print(f"Error: File {log_file_path} not found")
        return None, None
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None, None

# Example usage:
avg_rpm, max_rpm = analyze_rpm_from_log('logs/raceLog4.log') #file path to log you want to avg and max
if avg_rpm is not None:
    print(f"Average RPM: {avg_rpm}")
    print(f"Maximum RPM: {max_rpm}")

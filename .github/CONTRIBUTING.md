# Contributing to Drone GCS

Thank you for your interest in contributing to the Autonomous Fixed-Wing UAV Ground Control System! This document provides guidelines for contributing code, documentation, and bug reports.

---

## 🚀 Getting Started

### 1. Fork the Repository

Click "Fork" on GitHub to create your own copy.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR-OWN-USERNAME/Mission-Logic-Engine.git
cd drone-gcs
git remote add upstream https://github.com/Phoenix-UAV/Mission-Logic-Engine.git
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

**Branch naming conventions:**
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Code refactoring (no functional change)
- `test/` - Test additions or improvements
- `chore/` - Dependency updates, build changes, etc.

### 4. Setup Development Environment

Follow the OS-specific setup guide:
- [Windows](SETUP_WINDOWS.md)
- [Linux/Ubuntu](SETUP_LINUX.md)

---

## 📝 Development Workflow

### Writing Code

1. **Follow PEP 8 style guide** for Python code
2. **Write docstrings** for all functions and classes:
   ```python
   def calculate_intercept(position, velocity, target):
       """
       Calculate intercept point for pursuit algorithm.
       
       Args:
           position (tuple): Current UAV position (x, y, z)
           velocity (tuple): Current velocity (vx, vy, vz)
           target (tuple): Target position (x, y, z)
       
       Returns:
           tuple: Calculated intercept point (x, y, z)
       
       Raises:
           ValueError: If inputs are invalid
       """
       pass
   ```

3. **Use type hints**:
   ```python
   from typing import Tuple, List
   
   def process_telemetry(data: dict) -> Tuple[float, float, float]:
       """Process telemetry data."""
       pass
   ```

4. **Keep functions small** (< 50 lines preferred)
5. **Use meaningful variable names** (`px, py, pz` not `a, b, c`)

### Code Quality Tools

```bash
# Format code with Black
black src/

# Check style with Pylint
pylint src/

# Type checking with mypy
mypy src/

# Auto-fix common issues
autopep8 --in-place --aggressive src/

# All at once
black src/ && pylint src/ && mypy src/
```

### Testing

Write tests for all new features:

```python
# tests/unit/test_mission_logic.py
import unittest
from src.custom_gcs.mission.mission_engine import MissionEngine

class TestMissionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MissionEngine()
    
    def test_waypoint_calculation(self):
        """Test waypoint distance calculation."""
        result = self.engine.calculate_distance((0, 0, 0), (3, 4, 0))
        self.assertEqual(result, 5.0)
    
    def test_invalid_input(self):
        """Test handling of invalid input."""
        with self.assertRaises(ValueError):
            self.engine.calculate_distance(None, (3, 4, 0))

if __name__ == '__main__':
    unittest.main()
```

Run tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_mission_logic.py

# Run with coverage
pytest --cov=src/ tests/

# Run only fast tests
pytest -m "not slow"
```

---

## 📚 Writing Documentation

### Docstring Format

Use Google-style docstrings:

```python
def send_command_to_uav(command: str, params: dict) -> bool:
    """
    Send a control command to the UAV via DroneKit.
    
    This function wraps DroneKit commands with error handling
    and logging for all GCS commands.
    
    Args:
        command: MAVLink command name (e.g., 'arm', 'takeoff')
        params: Dictionary of command parameters
                {
                    'altitude': 50,  # meters
                    'speed': 15,     # m/s
                }
    
    Returns:
        True if command succeeded, False otherwise
    
    Raises:
        ValueError: If command is unknown
        DroneKitException: If connection lost during send
    
    Examples:
        >>> send_command_to_uav('takeoff', {'altitude': 30})
        True
        
        >>> send_command_to_uav('invalid_cmd', {})
        ValueError: Unknown command: invalid_cmd
    
    Note:
        Commands are queued and executed sequentially.
        Use timeout parameter for critical commands.
    """
    pass
```

### Markdown Documentation

Create guides in `/docs/guides/`:

```markdown
# How to Configure LoRa Telemetry

## Prerequisites
- LoRa LR900-F module
- USB-to-serial adapter
- MicoAir configuration tool (optional)

## Steps

1. Connect module via USB
2. Identify COM port
3. ...

## Troubleshooting

### Issue: Module not detected
**Solution**: ...
```

### Update Architecture Diagrams

If you modify system architecture:

1. Update relevant PlantUML files in `/docs/architecture/`
2. Regenerate images: `plantuml *.puml`
3. Update accompanying documentation

---

## 🔄 Committing Changes

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
**Scope**: Component affected (e.g., `mission`, `cv`, `telemetry`, `ros2`)
**Subject**: Imperative, not capitalized, no period

**Examples**:

```
feat(cv): add YOLO model selection UI

Allow users to choose between YOLOv8 nano, small, and medium
models based on their hardware constraints.

Fixes #42
```

```
fix(telemetry): resolve MAVProxy reconnection timeout

The telemetry publisher now properly handles reconnections
to MAVProxy if the connection drops during a mission.

Closes #56
```

### Commit Best Practices

```bash
# Stage changes
git add src/custom_gcs/mission_logic.py

# View what you're committing
git diff --staged

# Commit with message
git commit -m "feat(mission): implement waypoint interpolation"

# Sign commits (optional but recommended)
git commit -S -m "feat(mission): implement waypoint interpolation"

# Push to your fork
git push origin feature/your-feature-name
```

---

## 📤 Submitting a Pull Request

### Before Submitting

- [ ] Code follows PEP 8 style guide
- [ ] All tests pass: `pytest`
- [ ] Code coverage not decreased
- [ ] Docstrings added/updated
- [ ] Documentation updated (if needed)
- [ ] No merge conflicts with `main`
- [ ] Commit messages follow format

### Create Pull Request

1. Push your branch to your fork
2. Go to GitHub and click "Compare & pull request"
3. Fill in the PR template:

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #42

## How Has This Been Tested?
- [ ] Unit tests added
- [ ] Integration tests passed
- [ ] Manual testing on hardware

## Testing Environment
- OS: Windows 10 / Ubuntu 22.04 / macOS
- Python: 3.10 / 3.11
- ROS2: Humble / Iron

## Screenshots (if applicable)
[Add any relevant screenshots]

## Checklist
- [ ] Tests pass
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No breaking changes (or clearly noted)
```

### During Review

- Respond to feedback promptly
- Make requested changes in new commits
- Don't force-push unless asked
- Be respectful and constructive

---

## 🐛 Reporting Bugs

### Security Issues

**Do not** open a public issue for security vulnerabilities. Email the maintainer privately instead.

### Regular Bugs

Click "New Issue" and fill in the template:

```markdown
## Description
What's the bug? Be specific.

## Expected Behavior
What should happen?

## Actual Behavior
What actually happens?

## Steps to Reproduce
1. Start MAVProxy with...
2. Run custom GCS with...
3. Observe...

## Environment
- OS: Windows 10
- Python: 3.11
- ROS2: Humble
- Hardware: Pixhawk 6C + LoRa

## Logs
```
Paste relevant error messages or logs here
```

## Possible Solution
(Optional) Suggestions for fixing the bug
```

---

## 💡 Suggesting Features

Open an issue with "Feature Request" label:

```markdown
## Feature Description
What feature would you like to add?

## Use Case
Why is this feature important?

## Example
How would it be used?

## Alternatives
Are there other ways to solve this?
```

---

## 🤝 Code Review Guidelines

### For Authors

- Keep PRs focused (one feature per PR)
- Explain your reasoning in PR comments
- Link to related issues
- Respond to review comments promptly

### For Reviewers

- Be constructive and respectful
- Explain *why* something should change
- Suggest improvements, don't demand
- Test locally if possible
- Approve if quality meets standards

---

## 📖 Documentation Standards

### README

- Assume beginner-level audience
- Include setup steps
- Provide usage examples
- Link to detailed docs

### Guides

- Step-by-step instructions
- Include prerequisites
- Add troubleshooting section
- Use code examples

### API Documentation

- Docstrings in code
- Type hints for all parameters
- Examples for complex functions
- Link to architecture docs

### Architecture Diagrams

- Update when system changes
- Use PlantUML for consistency
- Keep legends and notes current
- Version diagrams with releases

---

## 🔄 Updating from Upstream

Keep your fork in sync:

```bash
# Fetch latest from original repo
git fetch upstream

# Rebase your branch
git rebase upstream/main

# Force push your changes (use carefully!)
git push -f origin feature/your-feature-name
```

---

## 📦 Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Creating a Release

1. Update version in `setup.py` and `__init__.py`
2. Update `CHANGELOG.md`
3. Tag release: `git tag v1.2.3`
4. Create release on GitHub
5. Merge to `main` branch

---

## ✨ Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README

---

## 📞 Questions?

- **Setup help**: Check [SETUP_WINDOWS.md](SETUP_WINDOWS.md) or [SETUP_LINUX.md](SETUP_LINUX.md)
- **Architecture questions**: See [PlantUML Guide](docs/architecture/PLANTUML_DIAGRAMS_GUIDE.md)
- **General questions**: Open GitHub Discussion
- **Chat**: Discord #drone-gcs channel

---

## 📜 Code of Conduct

We are committed to providing a welcoming and inclusive environment:

- Be respectful and constructive
- No harassment or discrimination
- Focus on ideas, not individuals
- Help others learn and grow

---

Thank you for contributing! 🙏 Your work helps make this project better.

---

*Last updated: June 2026*

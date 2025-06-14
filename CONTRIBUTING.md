# Contributing to Customer Service Multi-Agent System

Thank you for your interest in contributing to the Customer Service Multi-Agent System! We welcome contributions from the community and are excited to see what you'll bring to the project.

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- **Be respectful**: Treat everyone with respect and kindness
- **Be inclusive**: Welcome newcomers and help them get started
- **Be collaborative**: Work together to improve the project
- **Be constructive**: Provide helpful feedback and suggestions

## 🚀 Getting Started

### Prerequisites

Before contributing, make sure you have:
- Python 3.8+ installed
- Node.js 16+ installed
- Git configured with your name and email
- A GitHub account

### Setting Up Your Development Environment

1. **Fork the repository**
   ```bash
   # Click the "Fork" button on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/customer_service_mas.git
   cd customer_service_mas
   ```

2. **Add the upstream remote**
   ```bash
   git remote add upstream https://github.com/Ak-9647/customer_service_mas.git
   ```

3. **Set up the development environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   
   # Install frontend dependencies
   cd frontend
   npm install
   cd ..
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys for testing
   ```

5. **Run tests to ensure everything works**
   ```bash
   python -m pytest tests/
   npm test --prefix frontend
   ```

## 🛠️ Development Workflow

### Creating a New Feature

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run backend tests
   python -m pytest tests/
   
   # Run frontend tests
   npm test --prefix frontend
   
   # Run integration tests
   python test_enhanced_system.py
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```

5. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

**Examples:**
```
feat(agents): add new shipping inquiry agent
fix(refund): resolve eligibility calculation bug
docs: update API documentation
test(order): add tests for order lookup functionality
```

## 📝 Code Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/) guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Maximum line length: 88 characters (Black formatter)

**Example:**
```python
def process_refund(order_id: int, reason: str) -> Dict[str, Any]:
    """
    Process a refund request for the given order.
    
    Args:
        order_id: The ID of the order to refund
        reason: The reason for the refund request
        
    Returns:
        Dictionary containing refund processing results
        
    Raises:
        ValueError: If order_id is invalid
    """
    # Implementation here
    pass
```

### JavaScript/React Code Style

- Use ESLint configuration provided
- Use functional components with hooks
- Follow React best practices
- Use meaningful variable and function names

**Example:**
```javascript
const OrderStatus = ({ orderId }) => {
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    fetchOrderDetails(orderId);
  }, [orderId]);
  
  return (
    <div className="order-status">
      {/* Component JSX */}
    </div>
  );
};
```

## 🧪 Testing Guidelines

### Writing Tests

- Write tests for all new functionality
- Aim for high test coverage (>80%)
- Use descriptive test names
- Test both happy path and edge cases

### Test Structure

```python
def test_refund_processing_success():
    """Test successful refund processing for eligible order."""
    # Arrange
    order_id = 12345
    reason = "Product defective"
    
    # Act
    result = process_refund(order_id, reason)
    
    # Assert
    assert result["status"] == "success"
    assert "transaction_id" in result
```

### Running Tests

```bash
# Run all Python tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_agents.py -v

# Run with coverage
python -m pytest tests/ --cov=agents --cov-report=html

# Run frontend tests
npm test --prefix frontend

# Run integration tests
python test_enhanced_system.py
```

## 📚 Documentation

### Code Documentation

- Write clear docstrings for all functions and classes
- Include type hints
- Document complex algorithms and business logic
- Keep comments up to date with code changes

### API Documentation

- Update OpenAPI/Swagger documentation for API changes
- Include request/response examples
- Document error codes and responses

### README Updates

- Update README.md for new features
- Add usage examples
- Update installation instructions if needed

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear description** of the issue
2. **Steps to reproduce** the bug
3. **Expected behavior** vs actual behavior
4. **Environment details** (OS, Python version, etc.)
5. **Error messages** and stack traces
6. **Screenshots** if applicable

Use the bug report template:

```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 12.0]
- Python: [e.g., 3.9.7]
- Node.js: [e.g., 16.14.0]
- Browser: [e.g., Chrome 96.0]

## Additional Context
Any other relevant information
```

## 💡 Feature Requests

For feature requests, please:

1. **Check existing issues** to avoid duplicates
2. **Describe the problem** you're trying to solve
3. **Propose a solution** if you have one in mind
4. **Consider the scope** and impact on existing functionality

## 🔍 Code Review Process

### For Contributors

- Keep pull requests focused and small
- Write clear PR descriptions
- Respond to feedback promptly
- Update your branch if requested

### For Reviewers

- Be constructive and helpful
- Focus on code quality and maintainability
- Test the changes locally
- Approve when ready

### PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] Tests are written and passing
- [ ] Documentation is updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts
- [ ] PR description is clear

## 🏷️ Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. Update version numbers
2. Update CHANGELOG.md
3. Create release tag
4. Deploy to production
5. Announce release

## 🆘 Getting Help

If you need help:

1. **Check the documentation** first
2. **Search existing issues** for similar problems
3. **Ask in discussions** for general questions
4. **Create an issue** for bugs or feature requests

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: support@customer-service-mas.com

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to the Customer Service Multi-Agent System! 🚀 
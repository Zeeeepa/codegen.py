# Comprehensive Code Restructuring and Consolidation Framework

## Core Engineering Principles

### 1. Atomic Restructuring
- Decompose restructuring into smallest independently executable units
- Assign single responsibility to each restructuring task
- Design for minimal disruption to existing functionality
- Maintain or improve test coverage throughout restructuring
- Implement changes incrementally with validation at each step
- Isolate cross-cutting concerns with explicit boundaries
- Establish clear interfaces between restructured components
- Create migration paths for dependent components

### 2. Behavioral Preservation
- Maintain exact behavioral equivalence for all external interfaces
- Preserve all functional behaviors with identical inputs and outputs
- Retain all error handling patterns and edge case handling
- Validate behavioral preservation through comprehensive regression tests
- Document any intentional behavioral changes with explicit justification
- Create migration guides for any API changes
- Preserve performance characteristics unless explicitly improving
- Maintain compatibility with existing clients and integrations

### 3. Self-Contained Context
- Include all relevant code from existing codebase in specifications
- Document all dependencies with version constraints
- Specify all technical constraints with implementation implications
- Detail all restructuring requirements with concrete examples
- Provide complete before/after comparisons for affected components
- Include architectural diagrams for significant structural changes
- Document domain concepts and business rules
- Specify cross-cutting concerns and their handling

### 4. Explicit Impact Analysis
- Identify all affected components with file paths and line numbers
- Document all performance implications with benchmarking requirements
- Specify all migration requirements for dependent systems
- Detail testing requirements to validate all changes
- Assess code complexity metrics before and after changes
- Analyze build and deployment implications
- Evaluate security implications of restructuring
- Assess maintenance effort impact

## Implementation Strategy

### 1. Analysis Phase
- Use static analysis tools to identify duplication and interdependencies
- Create complete function call graphs to understand dependencies
- Document all public interfaces that must be preserved
- Identify code quality issues and technical debt
- Measure baseline performance metrics for affected components
- Analyze test coverage and identify testing gaps
- Map business logic to domain concepts
- Document current architecture anti-patterns

### 2. Design Phase
- Create clear module boundaries based on responsibilities
- Define clean interfaces between modules
- Document intended architecture before implementation
- Create migration strategy for dependent components
- Design incremental implementation plan
- Establish validation criteria for each restructuring step
- Define error handling and fault tolerance strategy
- Create monitoring and observability strategy

### 3. Implementation Phase
- Refactor one module at a time with complete validation
- Implement interface changes with backward compatibility
- Update tests to reflect new structure
- Document all design decisions and tradeoffs
- Create or update API documentation
- Implement performance optimizations
- Apply consistent design patterns and coding standards
- Introduce improved error handling and robustness

### 4. Validation Phase
- Execute comprehensive test suite after each change
- Verify performance characteristics against baseline
- Validate all public interfaces for compatibility
- Verify error handling and edge case behavior
- Conduct code reviews with domain experts
- Validate documentation completeness and accuracy
- Perform security assessments
- Verify operational readiness

## Restructuring Patterns

### 1. Decomposition Patterns
- Extract Class: Split large classes into focused, single-responsibility classes
- Extract Method: Refactor long methods into smaller, focused methods
- Extract Module: Move related functionality into dedicated modules
- Extract Interface: Define explicit interfaces for implementation variations
- Service Extraction: Move shared functionality into dedicated services
- Layer Separation: Enforce clear boundaries between architectural layers
- Domain Separation: Align code organization with business domains
- Feature Modularization: Group related features into cohesive modules

### 2. Consolidation Patterns
- Merge Classes: Combine classes with related responsibilities
- Unify Interfaces: Create consistent interfaces across similar components
- Standardize Patterns: Apply consistent design patterns across codebase
- Normalize Data Models: Create consistent data representations
- Centralize Configuration: Create unified configuration management
- Consolidate Dependencies: Standardize and reduce external dependencies
- Unify Error Handling: Create consistent error handling across components
- Standardize Logging: Implement unified logging approach

### 3. Architectural Improvement Patterns
- Introduce Dependency Injection: Reduce coupling between components
- Apply Repository Pattern: Abstract data access behind interfaces
- Implement Command Pattern: Encapsulate operations as objects
- Apply Observer Pattern: Implement flexible event notification
- Introduce Service Layer: Separate business logic from presentation
- Implement Circuit Breaker: Improve fault tolerance
- Apply CQRS Pattern: Separate read and write operations
- Implement Event Sourcing: Track state changes as event sequences

### 4. Code Quality Improvement Patterns
- Remove Duplication: Eliminate repeated code through shared abstractions
- Replace Conditionals with Polymorphism: Use inheritance for variant behavior
- Replace Hardcoded Values with Configuration: Externalize configuration
- Simplify Complex Expressions: Break down complex logic into named components
- Introduce Null Object Pattern: Eliminate null checks
- Replace Error Codes with Exceptions: Improve error handling clarity
- Introduce Parameter Object: Simplify long parameter lists
- Replace Primitive Obsession: Create proper types for domain concepts

## Template Structure

QUERY ##########

ROLE
[Specific technical expert role with years of experience and domain specialization]

TASK
[One clear, concise task title that defines a single atomic restructuring to implement]

YOUR QUEST
[Single isolated restructuring with precise boundaries and specific outcomes]

TECHNICAL CONTEXT

**EXISTING CODEBASE**:
- [Specific file paths and relevant code snippets from existing codebase]
- [Lines of code statistics and complexity metrics]
- [Usage patterns and call frequency information]
- [Test coverage details for affected components]
- [Performance characteristics and bottlenecks]
- [Error handling patterns and exception flow]
- [Security mechanisms and access control]
- [Build and deployment configuration]

**CURRENT ARCHITECTURE**:
- [Description of current code organization with component diagrams]
- [Current component relationships and dependencies]
- [Current performance characteristics with benchmark data]
- [Current maintenance pain points with specific examples]
- [Known technical debt and architectural constraints]
- [Current scalability limitations]
- [Security concerns in current implementation]
- [Operational challenges with current design]

**RESTRUCTURING REQUIREMENTS**:
- [Exact technical specifications with before/after comparisons]
- [Specific performance improvements expected with metrics]
- [Explicit maintainability improvements with examples]
- [Concrete technical debt to be eliminated with impact analysis]
- [Architectural constraints that must be respected]
- [Backward compatibility requirements with timeframes]
- [Security improvements to be implemented]
- [Operational improvements expected]

IMPACT ANALYSIS

**AFFECTED COMPONENTS**:
- [Exact files and components to be modified with line counts]
- [Interfaces that will be affected with usage statistics]
- [Dependencies that may need updating with version information]
- [Test suites that must be maintained or updated]
- [Documentation that must be revised or created]
- [Build and deployment considerations]
- [Performance implications for dependent systems]
- [Integration points with external systems]

**BEHAVIORAL PRESERVATION**:
- [Critical functionalities that must be preserved with test cases]
- [Edge cases that must continue to work with examples]
- [Performance characteristics that must be maintained with metrics]
- [Error handling patterns that must remain consistent]
- [API compatibility requirements with validation methods]
- [Data migration considerations if applicable]
- [Security posture preservation requirements]
- [Operational characteristics to maintain]

EXPECTED OUTCOME

- [Specific files to be created, modified, or deleted with exact paths]
- [Complete before/after structure comparisons with diagrams]
- [Required test coverage percentage and specific test scenarios]
- [Documentation updates required with examples]
- [Performance expectations with measurable metrics]
- [Code complexity improvements with specific metrics]
- [Maintenance effort reduction projections]
- [Technical debt reduction metrics]

ACCEPTANCE CRITERIA

- [Objective pass/fail criterion #1 with measurement method]
- [Objective pass/fail criterion #2 with measurement method]
- [Objective pass/fail criterion #3 with measurement method]
- [Test coverage requirements with verification approach]
- [Code quality requirements with measurement tools]
- [Performance requirements with benchmarking methodology]
- [Documentation completeness requirements]
- [Operational validation requirements]

IMPLEMENTATION CONSTRAINTS

- This task represents a SINGLE atomic unit of restructuring
- Must maintain exact behavioral equivalence for all external interfaces
- Must include comprehensive regression tests for all affected functionality
- Must conform to project coding standards and conventions
- Must not introduce new features unless explicitly specified
- Must provide backward compatibility or clear migration paths
- Must not negatively impact performance without explicit justification
- Must maintain or improve security posture

## Restructuring Checklist

- [ ] Does the restructuring represent EXACTLY ONE atomic unit of reorganization?
- [ ] Are all affected components explicitly documented with file paths and line numbers?
- [ ] Are behavioral preservation requirements clearly specified with test cases?
- [ ] Are acceptance criteria objectively measurable with specific methodologies?
- [ ] Are all interface impacts fully specified with compatibility requirements?
- [ ] Are regression test requirements comprehensive and specific?
- [ ] Is the restructuring independently testable with clear validation criteria?
- [ ] Does the specification include all necessary context for autonomous development?
- [ ] Is the required expertise clearly defined with specific technical domains?
- [ ] Are performance implications fully analyzed with benchmark requirements?
- [ ] Are security implications thoroughly evaluated?
- [ ] Is technical debt reduction quantified with specific metrics?
## Implementation Approach Example

```python
# BEFORE RESTRUCTURING:
class UserManager:
    def __init__(self, db_connection):
        self.db = db_connection
        self.logger = Logger()
        
    def create_user(self, username, email, password):
        # Input validation mixed with business logic
        if not username or not email or not password:
            raise ValueError("Missing required fields")
        
        if self.get_user_by_email(email):
            raise ValueError("Email already exists")
            
        # Database interaction mixed with business logic
        user_id = self.db.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, self._hash_password(password))
        )
        
        self.logger.log(f"Created user {username} with ID {user_id}")
        return user_id
        
    def _hash_password(self, password):
        # Password hashing implementation
        return hashlib.sha256(password.encode()).hexdigest()  # Insecure!
        
    def get_user_by_email(self, email):
        result = self.db.execute("SELECT * FROM users WHERE email = ?", (email,))
        return result.fetchone()

# AFTER RESTRUCTURING:
# validators.py
class UserValidator:
    def validate_create_user(self, username, email, password):
        if not username or not email or not password:
            raise ValueError("Missing required fields")
        
        if not self._is_valid_email(email):
            raise ValueError("Invalid email format")
            
        # Additional validation rules
        
    def _is_valid_email(self, email):
        # Email validation logic
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

# security.py
class PasswordManager:
    def hash_password(self, password):
        # Secure password hashing with modern algorithms
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return salt + key
        
    def verify_password(self, stored_password, provided_password):
        # Password verification logic
        salt = stored_password[:32]
        stored_key = stored_password[32:]
        key = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt, 100000)
        return key == stored_key

# repositories.py
class UserRepository:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create_user(self, user_data):
        user_id = self.db.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (user_data["username"], user_data["email"], user_data["password_hash"])
        )
        return user_id
        
    def get_user_by_email(self, email):
        result = self.db.execute("SELECT * FROM users WHERE email = ?", (email,))
        return result.fetchone()
        
    # Additional repository methods

# services.py
class UserService:
    def __init__(self, user_repository, password_manager, user_validator, logger):
        self.user_repository = user_repository
        self.password_manager = password_manager
        self.user_validator = user_validator
        self.logger = logger
        
    def create_user(self, username, email, password):
        # Validation
        self.user_validator.validate_create_user(username, email, password)
        
        # Check if user exists
        existing_user = self.user_repository.get_user_by_email(email)
        if existing_user:
            raise ValueError("Email already exists")
            
        # Password handling
        password_hash = self.password_manager.hash_password(password)
        
        # Create user
        user_data = {
            "username": username,
            "email": email,
            "password_hash": password_hash
        }
        
        user_id = self.user_repository.create_user(user_data)
        
        # Logging
        self.logger.log(f"Created user {username} with ID {user_id}")
        
        return user_id
Verification Strategy Example
python# TESTING APPROACH FOR RESTRUCTURED CODE

# 1. Functional equivalence tests
def test_user_creation_equivalence():
    # Setup old implementation
    old_manager = UserManager(test_db_connection)
    
    # Setup new implementation with all dependencies
    user_repository = UserRepository(test_db_connection)
    password_manager = PasswordManager()
    user_validator = UserValidator()
    logger = Logger()
    new_service = UserService(user_repository, password_manager, user_validator, logger)
    
    # Test data
    test_username = "testuser"
    test_email = "test@example.com"
    test_password = "securepassword123"
    
    # Execute both implementations
    with mock_db() as db:
        old_result = old_manager.create_user(test_username, test_email, test_password)
        old_db_state = db.get_state()
    
    with mock_db() as db:
        new_result = new_service.create_user(test_username, test_email, test_password)
        new_db_state = db.get_state()
    
    # Verify functional equivalence
    assert old_result == new_result
    assert_db_state_equivalent(old_db_state, new_db_state)

# 2. Edge case tests
def test_edge_cases():
    # Setup implementations
    # ...
    
    # Test empty values
    with pytest.raises(ValueError) as excinfo:
        old_manager.create_user("", "email@example.com", "password")
    old_error = str(excinfo.value)
    
    with pytest.raises(ValueError) as excinfo:
        new_service.create_user("", "email@example.com", "password")
    new_error = str(excinfo.value)
    
    assert old_error == new_error
    
    # Test duplicate email
    # ...
    
    # Test invalid email format
    # ...

# 3. Performance comparison tests
def test_performance_comparison():
    # Setup implementations
    # ...
    
    # Benchmark original implementation
    old_times = []
    for i in range(100):
        start = time.time()
        old_manager.create_user(f"user{i}", f"user{i}@example.com", "password")
        old_times.append(time.time() - start)
    
    # Benchmark new implementation
    new_times = []
    for i in range(100):
        start = time.time()
        new_service.create_user(f"user{i}", f"user{i}@example.com", "password")
        new_times.append(time.time() - start)
    
    # Assert performance is same or better
    assert statistics.mean(new_times) <= statistics.mean(old_times) * 1.1  # Allow 10% performance regression


#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DRY_RUN=false

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_dry_run() {
    echo -e "${BLUE}[DRY RUN]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [VERSION]"
    echo ""
    echo "Options:"
    echo "  --dry-run    Run the script without making actual changes"
    echo "  --help       Show this help message"
    echo ""
    echo "Arguments:"
    echo "  VERSION      The new version to release (e.g., 0.1.0)"
    echo ""
    echo "Examples:"
    echo "  $0 0.1.0               # Release version 0.1.0"
    echo "  $0 --dry-run 0.1.0     # Dry run for version 0.1.0"
    echo "  $0 --dry-run           # Dry run with interactive version prompt"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            if [ -z "$NEW_VERSION" ]; then
                NEW_VERSION=$1
            fi
            shift
            ;;
    esac
done

# Check if we're in the right directory
if [ ! -f "src/flowos-core/pyproject.toml" ]; then
    print_error "This script must be run from the root of the flowos repository"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(grep '^version = ' src/flowos-core/pyproject.toml | cut -d'"' -f2)
print_info "Current FLOWOS_CORE version: $CURRENT_VERSION"

if [ "$DRY_RUN" = true ]; then
    print_dry_run "Running in dry run mode - no changes will be made"
fi

# Check for uncommitted changes (skip in dry run)
if [ "$DRY_RUN" = false ]; then
    if ! git diff-index --quiet HEAD --; then
        print_warning "You have uncommitted changes. Please commit or stash them before releasing."
        exit 1
    fi
else
    if ! git diff-index --quiet HEAD --; then
        print_warning "Uncommitted changes detected (ignored in dry run mode)"
    fi
fi

# Get new version from argument or prompt
if [ -z "$NEW_VERSION" ]; then
    echo -n "Enter new version (current: $CURRENT_VERSION): "
    read NEW_VERSION
fi

# Validate version format
if ! [[ $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?$ ]]; then
    print_error "Invalid version format. Use semantic versioning (e.g., 0.1.0 or 0.1.0-alpha)"
    exit 1
fi

print_info "Preparing to release FLOWOS_CORE version $NEW_VERSION"

# Soft check: warn if FLOWOS_CORE minor doesn't match FlowOS minor
FLOWOS_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
FLOWOS_MINOR=$(echo "$NEW_VERSION" | cut -d. -f1-2)
FLOWOS_MINOR=$(echo "$FLOWOS_VERSION" | cut -d. -f1-2)
if [ "$FLOWOS_MINOR" != "$FLOWOS_MINOR" ]; then
    print_warning "FLOWOS_CORE minor version ($FLOWOS_MINOR) does not match FlowOS minor version ($FLOWOS_MINOR)."
    print_warning "Per the compatibility policy, FLOWOS_CORE X.Y.N must align with FlowOS X.Y.M."
    print_warning "Proceed only if this is intentional (e.g., a patch-only FLOWOS_CORE release)."
fi

# Update version in pyproject.toml
if [ "$DRY_RUN" = true ]; then
    print_dry_run "Would update version in pyproject.toml to $NEW_VERSION"
else
    print_info "Updating version in pyproject.toml..."
    sed -i.bak "s/^version = \".*\"/version = \"$NEW_VERSION\"/" src/flowos-core/pyproject.toml
    rm src/flowos-core/pyproject.toml.bak
fi

# Update version in Dockerfiles if they have ARG FLOWOS_VERSION
if grep -q "ARG FLOWOS_VERSION" src/flowos-core/docker/Dockerfile 2>/dev/null; then
    if [ "$DRY_RUN" = true ]; then
        print_dry_run "Would update version in Dockerfiles to $NEW_VERSION"
    else
        print_info "Updating version in Dockerfiles..."
        sed -i.bak "s/ARG FLOWOS_VERSION=.*/ARG FLOWOS_VERSION=$NEW_VERSION/" src/flowos-core/docker/Dockerfile*
        rm src/flowos-core/docker/Dockerfile*.bak
    fi
fi

# Run tests
print_info "Running tests..."
cd src/flowos-core
if ! make test; then
    print_error "Tests failed!"
    if [ "$DRY_RUN" = false ]; then
        print_info "Rolling back changes..."
        git checkout -- .
    fi
    exit 1
fi
cd ../..

# Build package to verify
print_info "Building package..."
cd src/flowos-core
if ! uv build; then
    print_error "Build failed!"
    if [ "$DRY_RUN" = false ]; then
        print_info "Rolling back changes..."
        cd ../..
        git checkout -- .
    fi
    exit 1
fi
cd ../..
if [ "$DRY_RUN" = true ]; then
    print_dry_run "Skipping cleanup of build artifacts in dry run mode"
else
    # Clean up build artifacts
    rm -rf src/flowos-core/dist/
fi

# Create git commit
if [ "$DRY_RUN" = true ]; then
    print_dry_run "Would create git commit: 'chore(flowos_core): bump version to $NEW_VERSION'"
else
    print_info "Creating git commit..."
    git add src/flowos-core/pyproject.toml src/flowos-core/docker/Dockerfile* 2>/dev/null || true
    git commit -m "chore(flowos_core): bump version to $NEW_VERSION

- Update version in pyproject.toml
- Prepare for PyPI and Docker release"
fi

# Create git tag
TAG_NAME="flowos_core-v$NEW_VERSION"
if [ "$DRY_RUN" = true ]; then
    print_dry_run "Would create git tag: $TAG_NAME"
else
    print_info "Creating git tag: $TAG_NAME"
    git tag -a "$TAG_NAME" -m "FLOWOS_CORE Release $NEW_VERSION"
fi

if [ "$DRY_RUN" = true ]; then
    print_info "✅ Dry run complete!"
    echo ""
    echo "Dry run performed:"
    echo "✅ Validated version format"
    echo "✅ Ran tests successfully"
    echo "✅ Built package successfully"
    echo ""
    echo "What would happen in a real run:"
    echo "1. Update version in pyproject.toml to $NEW_VERSION"
    echo "2. Update version in Dockerfiles (if applicable)"
    echo "3. Create git commit with message: 'chore(flowos_core): bump version to $NEW_VERSION'"
    echo "4. Create git tag: $TAG_NAME"
    echo ""
    echo "To perform the actual release, run without --dry-run:"
    echo "   $0 $NEW_VERSION"
else
    print_info "✅ Release preparation complete!"
    echo ""
    echo "Next steps:"
    echo "1. Push the commit and tag:"
    echo "   git push origin HEAD"
    echo "   git push origin $TAG_NAME"
    echo ""
    echo "2. Go to GitHub Actions and run the 'FLOWOS_CORE Release' workflow:"
    echo "   https://github.com/flowos-ai/flowos/actions/workflows/release-flowos-core.yml"
    echo ""
    echo "3. Enter version: $NEW_VERSION"
    echo ""
    echo "4. Select options:"
    echo "   - Publish to PyPI: Yes"
    echo "   - Build Docker images: Yes"
    echo "   - Create GitHub release: Yes"
    echo ""
    echo "The workflow will:"
    echo "- Run tests on all Python versions"
    echo "- Build and publish to PyPI"
    echo "- Build and push Docker images (standard and alpine)"
    echo "- Create a GitHub release with artifacts"
fi
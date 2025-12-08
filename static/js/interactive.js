// Interactive features for Receipt Scanner

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize all interactive features
    initLoadingOverlay();
    initFormSubmissions();
    initImageZoom();
    initFileUpload();
    initAnimations();
    initSearchEnhancements();
    initTooltips();
    
    console.log('Receipt Scanner interactive features loaded');
});

// Loading overlay for async operations
function initLoadingOverlay() {
    // Create loading overlay if it doesn't exist
    if (!document.querySelector('.loading-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">Processing...</div>
        `;
        document.body.appendChild(overlay);
    }
}

// Show loading overlay
function showLoading(message = 'Processing...') {
    const overlay = document.querySelector('.loading-overlay');
    const text = overlay.querySelector('.loading-text');
    if (text) text.textContent = message;
    overlay.classList.add('active');
}

// Hide loading overlay
function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    overlay.classList.remove('active');
}

// Enhanced form submissions with loading states
function initFormSubmissions() {
    // Scan form
    const scanForm = document.querySelector('form[action*="scan"]');
    if (scanForm && scanForm.querySelector('button[type="submit"]')) {
        scanForm.addEventListener('submit', function(e) {
            showLoading('Capturing & Processing Receipt...');
        });
    }
    
    // Upload form
    const uploadForm = document.querySelector('form[enctype="multipart/form-data"]');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const fileInput = uploadForm.querySelector('input[type="file"]');
            if (fileInput && fileInput.files.length > 0) {
                showLoading('Uploading & Processing Receipt...');
            } else {
                e.preventDefault();
                alert('Please select a file to upload');
            }
        });
    }
    
    // Receipt detail save form
    const detailForm = document.querySelector('form[method="post"]');
    if (detailForm && window.location.pathname.includes('/receipts/')) {
        detailForm.addEventListener('submit', function(e) {
            showLoading('Saving Receipt...');
        });
    }
}

// Image zoom functionality
function initImageZoom() {
    const images = document.querySelectorAll('.img-fluid');
    
    // Create modal if it doesn't exist
    if (!document.querySelector('.image-modal')) {
        const modal = document.createElement('div');
        modal.className = 'image-modal';
        modal.innerHTML = '<img src="" alt="Zoomed image">';
        document.body.appendChild(modal);
        
        // Close modal on click
        modal.addEventListener('click', function() {
            modal.classList.remove('active');
        });
    }
    
    const modal = document.querySelector('.image-modal');
    const modalImg = modal.querySelector('img');
    
    images.forEach(img => {
        img.style.cursor = 'zoom-in';
        img.addEventListener('click', function() {
            modalImg.src = this.src;
            modal.classList.add('active');
        });
    });
    
    // ESC key to close modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            modal.classList.remove('active');
        }
    });
}

// Enhanced file upload with drag and drop
function initFileUpload() {
    const fileInput = document.querySelector('input[type="file"]');
    if (!fileInput) return;
    
    const form = fileInput.closest('form');
    if (!form) return;
    
    // Create drag and drop zone
    const uploadZone = document.createElement('div');
    uploadZone.className = 'file-upload-zone mb-3';
    uploadZone.innerHTML = `
        <div class="file-upload-icon">📄</div>
        <h5>Drop receipt image here</h5>
        <p class="text-muted">or click to browse</p>
        <p class="text-muted small">Supports: JPG, PNG, GIF</p>
    `;
    
    // Replace or wrap the file input
    const fileInputContainer = fileInput.closest('.mb-3');
    if (fileInputContainer) {
        fileInput.style.display = 'none';
        fileInputContainer.insertBefore(uploadZone, fileInput);
    }
    
    // Click to open file dialog
    uploadZone.addEventListener('click', function() {
        fileInput.click();
    });
    
    // File selected feedback
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            const fileName = this.files[0].name;
            uploadZone.querySelector('h5').textContent = '✓ ' + fileName;
            uploadZone.style.borderColor = 'var(--accent-green)';
            uploadZone.style.background = 'rgba(122, 159, 126, 0.1)';
        }
    });
    
    // Drag and drop events
    uploadZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            const fileName = files[0].name;
            uploadZone.querySelector('h5').textContent = '✓ ' + fileName;
            uploadZone.style.borderColor = 'var(--accent-green)';
            uploadZone.style.background = 'rgba(122, 159, 126, 0.1)';
        }
    });
}

// Animate stats cards on dashboard
function initAnimations() {
    // Add animation class to stats cards
    const statsCards = document.querySelectorAll('.row .col-md-4 .card');
    statsCards.forEach((card, index) => {
        card.classList.add('stats-card');
        card.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Animate numbers on stats cards
    const statNumbers = document.querySelectorAll('.display-6');
    statNumbers.forEach(stat => {
        const text = stat.textContent;
        const number = parseFloat(text.replace(/[^0-9.]/g, ''));
        
        if (!isNaN(number)) {
            stat.textContent = text.replace(number, '0');
            animateNumber(stat, 0, number, 1000, text);
        }
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
}

// Animate number counter
function animateNumber(element, start, end, duration, template) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        
        const formatted = template.includes('$') 
            ? current.toFixed(2) 
            : Math.round(current);
        element.textContent = template.replace(/[0-9.]+/, formatted);
    }, 16);
}

// Enhanced search with live feedback
function initSearchEnhancements() {
    const searchInput = document.querySelector('input[type="search"]');
    if (!searchInput) return;
    
    // Add search icon
    const searchContainer = searchInput.parentElement;
    if (searchContainer && !searchContainer.classList.contains('search-container')) {
        searchContainer.classList.add('search-container');
    }
    
    // Live search feedback
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        
        const value = this.value.trim();
        if (value.length > 0) {
            this.style.borderColor = 'var(--accent-blue)';
            
            // Debounce: highlight matching rows
            searchTimeout = setTimeout(() => {
                highlightSearchResults(value);
            }, 300);
        } else {
            this.style.borderColor = '';
            clearHighlights();
        }
    });
}

// Highlight search results in table
function highlightSearchResults(query) {
    const rows = document.querySelectorAll('tbody tr');
    const lowerQuery = query.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(lowerQuery)) {
            row.style.background = 'rgba(212, 165, 116, 0.1)';
            row.style.borderLeft = '3px solid var(--accent-warm)';
        } else {
            row.style.opacity = '0.5';
        }
    });
}

// Clear search highlights
function clearHighlights() {
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        row.style.background = '';
        row.style.borderLeft = '';
        row.style.opacity = '';
    });
}

// Initialize tooltips for better UX
function initTooltips() {
    // Add tooltips to sortable table headers
    const sortHeaders = document.querySelectorAll('th a[href*="sort"]');
    sortHeaders.forEach(header => {
        header.title = 'Click to sort';
        header.style.cursor = 'pointer';
    });
    
    // Add tooltips to action buttons
    const actionButtons = document.querySelectorAll('.btn');
    actionButtons.forEach(button => {
        if (!button.title && button.textContent.trim()) {
            // Add subtle visual feedback
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
            });
            button.addEventListener('mouseleave', function() {
                this.style.transform = '';
            });
        }
    });
}

// Form validation enhancements
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = 'var(--accent-red)';
                    
                    // Remove error styling on input
                    field.addEventListener('input', function() {
                        this.style.borderColor = '';
                    }, { once: true });
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields');
            }
        });
    });
}

// Auto-dismiss alerts after 5 seconds
setTimeout(function() {
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        alerts.forEach(alert => {
            if (!alert.classList.contains('alert-danger')) {
                const closeButton = alert.querySelector('.btn-close');
                if (closeButton) {
                    closeButton.click();
                }
            }
        });
    }
}, 5000);

// Add ripple effect to buttons
document.addEventListener('click', function(e) {
    if (e.target.matches('.btn')) {
        const button = e.target;
        const ripple = document.createElement('span');
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(255, 255, 255, 0.6)';
        ripple.style.width = ripple.style.height = '100px';
        ripple.style.left = e.offsetX - 50 + 'px';
        ripple.style.top = e.offsetY - 50 + 'px';
        ripple.style.pointerEvents = 'none';
        ripple.style.animation = 'ripple 0.6s ease-out';
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }
});

// Add keyboard shortcut hints
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        const searchInput = document.querySelector('input[type="search"]');
        if (searchInput) {
            e.preventDefault();
            searchInput.focus();
            searchInput.select();
        }
    }
});

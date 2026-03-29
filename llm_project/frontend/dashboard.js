document.addEventListener('DOMContentLoaded', function () {
    // ═══════════════════════ DOM ELEMENTS ═══════════════════════
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const newChatBtn = document.getElementById('newChatBtn');
    const chatHistory = document.getElementById('chatHistory');
    const chatHeader = document.getElementById('chatHeader');
    const welcomeMessage = document.getElementById('welcomeMessage');
    const chatArea = document.getElementById('chatArea');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const profileIcon = document.getElementById('profileIcon');
    const profilePopover = document.getElementById('profilePopover');
    const popoverUserName = document.getElementById('popoverUserName');
    const profileUserName = document.getElementById('profileUserName');
    const profileInitials = document.getElementById('profileInitials');
    const SignOut = document.getElementById('SignOut');
    const attachBtn = document.getElementById('attachBtn');
    const attachPopover = document.getElementById('attachPopover');
    const customModal = document.getElementById('customModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    const modalConfirmBtn = document.getElementById('modalConfirmBtn');
    const modalCancelBtn = document.getElementById('modalCancelBtn');
    const llmModelSelect = document.getElementById('llmModelSelect');
    const fileInput = document.getElementById('fileInput');
    const ingestFileInput = document.getElementById('ingestFileInput');
    const filePreviewContainer = document.getElementById('filePreviewContainer');
    const toastContainer = document.getElementById('toastContainer');

    // ═══════════════════════ CONFIG ═══════════════════════
    const API_BASE_URL = 'http://localhost:8000';
    const userName = "Ayush Aman";
    let chatSessions = {};
    let currentSessionId = null;
    let modalConfirmCallback = null;
    let isWaitingForResponse = false;

    // ═══════════════════════ TOAST NOTIFICATIONS ═══════════════════════
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        toastContainer.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    // ═══════════════════════ USER SETUP ═══════════════════════
    function setupUser() {
        const nameParts = userName.split(' ');
        const firstName = nameParts[0];
        const initials = nameParts.map(n => n[0]).join('');
        welcomeMessage.textContent = `Welcome, ${firstName}! Ask about Government Schemes 🇮🇳`;
        popoverUserName.textContent = userName;
        profileUserName.textContent = userName;
        profileInitials.textContent = initials;
    }

    // ═══════════════════════ SESSION MANAGEMENT ═══════════════════════
    function createNewSession(makeActive = true) {
        const sessionId = `session_${Date.now()}`;
        chatSessions[sessionId] = {
            title: 'New Chat',
            messages: [
                { role: 'assistant', content: 'Namaste! 🙏 I\'m your Citizen Services Assistant. Ask me about Indian Government schemes — eligibility, benefits, documents, application steps, or find nearest service centers.', route: null, sources: [] }
            ]
        };
        if (makeActive) {
            currentSessionId = sessionId;
        }
        renderChatHistory();
        renderMessagesForSession(currentSessionId);
    }

    function renderChatHistory() {
        chatHistory.innerHTML = '';
        Object.keys(chatSessions).forEach(sessionId => {
            const session = chatSessions[sessionId];
            const topicEl = document.createElement('div');
            topicEl.className = 'sidebar-topic';
            topicEl.dataset.sessionId = sessionId;

            const titleEl = document.createElement('span');
            titleEl.className = 'title';
            titleEl.textContent = session.title;

            const menuBtn = document.createElement('button');
            menuBtn.className = 'topic-menu-btn';
            menuBtn.innerHTML = '⋯';

            const menu = document.createElement('div');
            menu.className = 'topic-menu';
            menu.innerHTML = `
                <div class="topic-menu-item" data-action="rename">Rename</div>
                <div class="topic-menu-item" data-action="delete">Delete</div>
            `;

            topicEl.appendChild(titleEl);
            topicEl.appendChild(menuBtn);
            topicEl.appendChild(menu);

            if (sessionId === currentSessionId) {
                topicEl.classList.add('active');
            }

            titleEl.addEventListener('click', () => {
                currentSessionId = sessionId;
                renderMessagesForSession(sessionId);
                renderChatHistory();
            });

            menuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                closeAllMenus();
                menu.classList.toggle('show');
            });

            menu.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = e.target.dataset.action;
                if (action === 'rename') handleRename(sessionId);
                else if (action === 'delete') handleDelete(sessionId);
                menu.classList.remove('show');
            });

            chatHistory.appendChild(topicEl);
        });
    }

    function closeAllMenus() {
        document.querySelectorAll('.topic-menu.show').forEach(m => m.classList.remove('show'));
        attachPopover.classList.remove('show');
    }

    // ═══════════════════════ MESSAGE RENDERING ═══════════════════════
    function renderMessagesForSession(sessionId) {
        chatArea.innerHTML = '';
        const session = chatSessions[sessionId];
        if (session) {
            chatHeader.classList.toggle('hidden', session.messages.length > 1);
            session.messages.forEach(msg => addMessageToDOM(msg.role, msg.content, msg.route, msg.sources));
        }
    }

    function addMessageToCurrentSession(role, content, route = null, sources = []) {
        if (!currentSessionId || !chatSessions[currentSessionId]) return;

        chatSessions[currentSessionId].messages.push({ role, content, route, sources });

        if (role === 'user' && chatSessions[currentSessionId].messages.length === 2) {
            chatHeader.classList.add('hidden');
        }

        const messages = chatSessions[currentSessionId].messages;
        if (role === 'user' && messages.filter(m => m.role === 'user').length === 1) {
            const newTitle = content.substring(0, 30) + (content.length > 30 ? '...' : '');
            chatSessions[currentSessionId].title = newTitle;
            renderChatHistory();
        }

        addMessageToDOM(role, content, route, sources);
    }

    function addMessageToDOM(role, content, route = null, sources = []) {
        const messageWrapper = document.createElement('div');
        messageWrapper.className = `chat-message ${role}`;

        const messageBubble = document.createElement('div');
        messageBubble.className = 'chat-bubble';

        // Route badge for assistant messages
        if (role === 'assistant' && route) {
            const badge = document.createElement('div');
            badge.className = `route-badge ${route}`;
            const icons = { rag: '📚', web: '🌐', eligibility: '✅' };
            const labels = { rag: 'Knowledge Base', web: 'Web Search', eligibility: 'Eligibility Check' };
            badge.innerHTML = `${icons[route] || ''} ${labels[route] || route}`;
            messageBubble.appendChild(badge);
        }

        // Message content
        const contentDiv = document.createElement('div');
        contentDiv.innerHTML = formatContent(content);
        messageBubble.appendChild(contentDiv);

        // Sources
        if (role === 'assistant' && sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'sources-section';
            sourcesDiv.innerHTML = '<div class="sources-title">📎 Sources</div>';
            sources.forEach(src => {
                const item = document.createElement('div');
                item.className = 'source-item';
                if (src.url) {
                    item.innerHTML = `🔗 <a href="${src.url}" target="_blank">${src.title || src.url}</a>`;
                } else if (src.source) {
                    item.textContent = `📄 ${src.source}${src.page ? ' (Page ' + src.page + ')' : ''}`;
                } else if (src.tools_used) {
                    item.textContent = `🔧 Tools: ${src.tools_used.join(', ')}`;
                }
                sourcesDiv.appendChild(item);
            });
            messageBubble.appendChild(sourcesDiv);
        }

        messageWrapper.appendChild(messageBubble);
        chatArea.appendChild(messageWrapper);
        scrollToBottom();
    }

    function formatContent(content) {
        if (!content) return '';
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/^\s*[-•]\s+(.+)/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
            .replace(/^\s*(\d+)\.\s+(.+)/gm, '<li>$2</li>')
            .replace(/\n/g, '<br>');
    }

    function addTypingIndicator() {
        const wrapper = document.createElement('div');
        wrapper.className = 'chat-message assistant';
        wrapper.id = 'typingIndicator';
        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble';
        bubble.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        wrapper.appendChild(bubble);
        chatArea.appendChild(wrapper);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) indicator.remove();
    }

    function scrollToBottom() {
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    // ═══════════════════════ API CALLS ═══════════════════════
    async function fetchChatResponse(userInput) {
        const payload = {
            query: userInput,
            session_id: currentSessionId,
            model: llmModelSelect.value === 'gemini' ? null : llmModelSelect.value,
        };

        try {
            addTypingIndicator();
            isWaitingForResponse = true;
            sendBtn.disabled = true;

            const response = await fetch(`${API_BASE_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            removeTypingIndicator();

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText.substring(0, 150)}`);
            }

            const data = await response.json();
            addMessageToCurrentSession('assistant', data.answer, data.route, data.sources);

        } catch (error) {
            removeTypingIndicator();
            console.error('Chat error:', error);
            addMessageToCurrentSession('assistant', `⚠️ Error: ${error.message}`);
            showToast('Failed to get response', 'error');
        } finally {
            isWaitingForResponse = false;
            sendBtn.disabled = false;
        }
    }

    async function ingestFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            showToast(`Ingesting "${file.name}"...`, 'info');

            const response = await fetch(`${API_BASE_URL}/api/ingest`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText.substring(0, 100)}`);
            }

            const data = await response.json();
            showToast(`✅ Ingested ${data.chunks_ingested} chunks from "${file.name}"`, 'success');

        } catch (error) {
            console.error('Ingest error:', error);
            showToast(`❌ Ingestion failed: ${error.message}`, 'error');
        }
    }

    async function fetchSchemes(query) {
        try {
            addTypingIndicator();
            const response = await fetch(`${API_BASE_URL}/api/schemes?q=${encodeURIComponent(query)}`);
            removeTypingIndicator();

            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            addMessageToCurrentSession('assistant', data.results, 'rag', []);

        } catch (error) {
            removeTypingIndicator();
            showToast('Failed to fetch schemes', 'error');
        }
    }

    async function checkEligibility(payload) {
        try {
            addTypingIndicator();
            const model = llmModelSelect.value === 'gemini' ? null : llmModelSelect.value;
            payload.model = model;
            const response = await fetch(`${API_BASE_URL}/api/eligibility`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            removeTypingIndicator();

            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            addMessageToCurrentSession('assistant', data.answer, 'eligibility', data.sources);

        } catch (error) {
            removeTypingIndicator();
            showToast('Eligibility check failed', 'error');
        }
    }

    // ═══════════════════════ MODALS ═══════════════════════
    function showModal(config) {
        modalTitle.textContent = config.title;
        modalBody.innerHTML = config.body;
        modalConfirmBtn.textContent = config.confirmText;
        modalConfirmCallback = config.onConfirm;
        customModal.style.display = 'flex';
        const input = modalBody.querySelector('input');
        if (input) { input.focus(); input.select(); }
    }

    function hideModal() {
        customModal.style.display = 'none';
        modalConfirmCallback = null;
    }

    function handleRename(sessionId) {
        showModal({
            title: 'Rename Chat',
            body: `<input type="text" id="renameInput" class="modal-input" value="${chatSessions[sessionId].title}">`,
            confirmText: 'Rename',
            onConfirm: () => {
                const val = document.getElementById('renameInput').value.trim();
                if (val) {
                    chatSessions[sessionId].title = val;
                    renderChatHistory();
                }
            }
        });
    }

    function handleDelete(sessionId) {
        showModal({
            title: 'Delete Chat',
            body: `<p>Are you sure you want to delete this chat?</p>`,
            confirmText: 'Delete',
            onConfirm: () => {
                delete chatSessions[sessionId];
                if (currentSessionId === sessionId) {
                    const remaining = Object.keys(chatSessions);
                    if (remaining.length > 0) {
                        currentSessionId = remaining[0];
                    } else {
                        createNewSession();
                        return;
                    }
                }
                renderChatHistory();
                renderMessagesForSession(currentSessionId);
            }
        });
    }

    // ═══════════════════════ FILE HANDLING ═══════════════════════
    function clearFilePreview() {
        filePreviewContainer.innerHTML = '';
        filePreviewContainer.classList.add('hidden');
    }

    function renderPreview(file) {
        filePreviewContainer.innerHTML = '';
        const previewEl = document.createElement('div');
        previewEl.className = 'file-preview-item';

        const icon = document.createElement('div');
        icon.className = 'file-icon';
        icon.textContent = file.name.split('.').pop().toUpperCase();
        previewEl.appendChild(icon);

        const nameSpan = document.createElement('span');
        nameSpan.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        nameSpan.className = 'file-name';
        previewEl.appendChild(nameSpan);

        const removeBtn = document.createElement('button');
        removeBtn.className = 'file-remove-btn';
        removeBtn.innerHTML = '×';
        removeBtn.onclick = () => {
            fileInput.value = null;
            clearFilePreview();
        };
        previewEl.appendChild(removeBtn);

        filePreviewContainer.appendChild(previewEl);
        filePreviewContainer.classList.remove('hidden');
    }

    // ═══════════════════════ EVENT LISTENERS ═══════════════════════
    sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('collapsed'));
    newChatBtn.addEventListener('click', () => createNewSession());

    // Suggestion chips
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const query = chip.dataset.query;
            chatInput.value = query;
            chatForm.dispatchEvent(new Event('submit'));
        });
    });

    // Quick action buttons
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            if (action === 'schemes') {
                chatInput.value = 'List all available government schemes';
                chatForm.dispatchEvent(new Event('submit'));
            } else if (action === 'eligibility') {
                showModal({
                    title: 'Check Eligibility',
                    body: `
                        <div style="display: flex; flex-direction: column; gap: 10px;">
                            <input type="text" id="eligQuery" class="modal-input" placeholder="Question (e.g., Am I eligible?)" required>
                            <input type="text" id="eligScheme" class="modal-input" placeholder="Scheme Name (e.g., PM Kisan)">
                            <input type="number" id="eligAge" class="modal-input" placeholder="Age (e.g., 25)">
                            <input type="number" id="eligIncome" class="modal-input" placeholder="Annual Income (₹)">
                            <input type="text" id="eligState" class="modal-input" placeholder="State/Resident (e.g., UP)">
                            <input type="text" id="eligCategory" class="modal-input" placeholder="Category (e.g., Farmer, SC/ST)">
                        </div>
                    `,
                    confirmText: 'Check Eligibility',
                    onConfirm: () => {
                        const payload = {
                            query: document.getElementById('eligQuery').value.trim() || 'Check my eligibility for government schemes.',
                            scheme_name: document.getElementById('eligScheme').value.trim() || null,
                            age: parseInt(document.getElementById('eligAge').value) || null,
                            income: parseFloat(document.getElementById('eligIncome').value) || null,
                            state: document.getElementById('eligState').value.trim() || null,
                            category: document.getElementById('eligCategory').value.trim() || null
                        };

                        let uiMsg = `**Eligibility Check**\n**Query:** ${payload.query}`;
                        if (payload.scheme_name) uiMsg += `\n**Scheme:** ${payload.scheme_name}`;
                        if (payload.age) uiMsg += `\n**Age:** ${payload.age}`;
                        if (payload.income) uiMsg += `\n**Income:** ₹${payload.income}`;
                        if (payload.state) uiMsg += `\n**State:** ${payload.state}`;
                        if (payload.category) uiMsg += `\n**Category:** ${payload.category}`;

                        addMessageToCurrentSession('user', uiMsg);
                        checkEligibility(payload);
                    }
                });
            } else if (action === 'ingest') {
                ingestFileInput.click();
            }
        });
    });

    // Attach popover
    attachBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        closeAllMenus();
        attachPopover.classList.toggle('show');
    });

    attachPopover.addEventListener('click', (e) => {
        const item = e.target.closest('.attach-popover-item');
        if (!item) return;
        const type = item.dataset.type;
        if (type === 'Documents') {
            fileInput.accept = '.pdf,.txt,.md';
            fileInput.click();
        } else if (type === 'Ingest') {
            ingestFileInput.click();
        }
        attachPopover.classList.remove('show');
    });

    fileInput.addEventListener('change', function () {
        if (this.files.length > 0) renderPreview(this.files[0]);
        else clearFilePreview();
    });

    ingestFileInput.addEventListener('change', function () {
        if (this.files.length > 0) {
            ingestFile(this.files[0]);
            this.value = null;
        }
    });

    // Profile
    profileIcon.addEventListener('click', () => {
        closeAllMenus();
        profilePopover.classList.toggle('show');
    });

    SignOut.addEventListener('click', () => window.location.href = 'index.html');

    // Global click handler
    window.addEventListener('click', (e) => {
        if (!profileIcon.contains(e.target) && !profilePopover.contains(e.target)) {
            profilePopover.classList.remove('show');
        }
        if (!e.target.closest('.topic-menu-btn') && !e.target.closest('.topic-menu') &&
            !e.target.closest('#attachBtn') && !e.target.closest('#attachPopover')) {
            closeAllMenus();
        }
    });

    // Modal listeners
    modalConfirmBtn.addEventListener('click', () => {
        if (modalConfirmCallback) modalConfirmCallback();
        hideModal();
    });
    modalCancelBtn.addEventListener('click', hideModal);
    customModal.addEventListener('click', (e) => {
        if (e.target === customModal) hideModal();
    });

    // ═══════════════════════ FORM SUBMIT ═══════════════════════
    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();
        if (isWaitingForResponse) return;

        const userInput = chatInput.value.trim();
        const file = fileInput.files[0];

        if (!userInput && !file) return;

        let messageContent = userInput;
        if (file) {
            messageContent += `\n📎 [Attached: ${file.name}]`;
        }

        addMessageToCurrentSession('user', messageContent);

        // Clear inputs
        chatInput.value = '';
        fileInput.value = null;
        clearFilePreview();

        // If file is attached, ingest it first, then chat
        if (file) {
            ingestFile(file).then(() => {
                if (userInput) fetchChatResponse(userInput);
            });
        } else {
            fetchChatResponse(userInput);
        }
    });

    // Enter key handling
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // ═══════════════════════ INIT ═══════════════════════
    setupUser();
    createNewSession();
    chatInput.focus();
});

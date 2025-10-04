document.addEventListener('DOMContentLoaded', function() {
            // --- DOM Elements ---
            const sidebar = document.getElementById('sidebar');
            const sidebarToggle = document.getElementById('sidebarToggle');
            const newChatBtn = document.getElementById('newChatBtn');
            const chatHistory = document.getElementById('chatHistory');
            const chatHeader = document.getElementById('chatHeader');
            const welcomeMessage = document.getElementById('welcomeMessage');
            const chatArea = document.getElementById('chatArea');
            const chatForm = document.getElementById('chatForm');
            const chatInput = document.getElementById('chatInput');
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

            // --- User & State Management ---
            // In a real app, you'd get this from localStorage after login
            const userName = "Ayush Aman"; 
            let chatSessions = {};
            let currentSessionId = null;
            let modalConfirmCallback = null;

            // --- Functions ---
            function setupUser() {
                const nameParts = userName.split(' ');
                const firstName = nameParts[0];
                const initials = nameParts.map(n => n[0]).join('');
                
                welcomeMessage.textContent = `Welcome, ${firstName}!`;
                popoverUserName.textContent = userName;
                profileUserName.textContent = userName;
                profileInitials.textContent = initials;
            }

            function createNewSession(makeActive = true) {
                const sessionId = `session_${Date.now()}`;
                chatSessions[sessionId] = {
                    title: 'New Chat',
                    messages: [
                        { role: 'assistant', content: 'Hi there! How can I help you today?' }
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
                    menuBtn.innerHTML = '...';
                    
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

                    // Event Listeners
                    titleEl.addEventListener('click', () => {
                        currentSessionId = sessionId;
                        renderMessagesForSession(sessionId);
                        renderChatHistory(); // Re-render to update active state
                    });

                    menuBtn.addEventListener('click', (e) => {
                        e.stopPropagation(); // Prevent topicEl click event
                        closeAllMenus();
                        menu.classList.toggle('show');
                    });
                    
                    menu.addEventListener('click', (e) => {
                         e.stopPropagation();
                        const action = e.target.dataset.action;
                        if (action === 'rename') {
                            handleRename(sessionId);
                        } else if (action === 'delete') {
                            handleDelete(sessionId);
                        }
                        menu.classList.remove('show');
                    });

                    chatHistory.appendChild(topicEl);
                });
            }

            function closeAllMenus() {
                document.querySelectorAll('.topic-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
                attachPopover.classList.remove('show');
            }

            function renderMessagesForSession(sessionId) {
                chatArea.innerHTML = '';
                const session = chatSessions[sessionId];
                if (session) {
                    // Show header only for new, empty chats
                    if (session.messages.length > 1) {
                        chatHeader.classList.add('hidden');
                    } else {
                        chatHeader.classList.remove('hidden');
                    }
                    session.messages.forEach(msg => addMessageToDOM(msg.role, msg.content));
                }
            }
            
            function addMessageToCurrentSession(role, content) {
                 if (!currentSessionId || !chatSessions[currentSessionId]) return;
                
                chatSessions[currentSessionId].messages.push({ role, content });

                // Hide header on first user message
                if (role === 'user' && chatSessions[currentSessionId].messages.length === 2) {
                    chatHeader.classList.add('hidden');
                }

                // Update title if it's the first user message
                const messages = chatSessions[currentSessionId].messages;
                if(role === 'user' && messages.filter(m => m.role === 'user').length === 1) {
                    const newTitle = content.substring(0, 25) + (content.length > 25 ? '...' : '');
                    chatSessions[currentSessionId].title = newTitle;
                    renderChatHistory();
                }

                addMessageToDOM(role, content);
            }

            function addMessageToDOM(role, content) {
                const messageWrapper = document.createElement('div');
                messageWrapper.className = `chat-message ${role}`;
                
                const messageBubble = document.createElement('div');
                messageBubble.className = 'chat-bubble';
                messageBubble.textContent = content;

                messageWrapper.appendChild(messageBubble);
                chatArea.appendChild(messageWrapper);
                scrollToBottom();
            }


            function scrollToBottom() {
                chatArea.scrollTop = chatArea.scrollHeight;
            }

            // --- Modal Functions ---
            function showModal(config) {
                modalTitle.textContent = config.title;
                modalBody.innerHTML = config.body;
                modalConfirmBtn.textContent = config.confirmText;
                modalConfirmCallback = config.onConfirm;
                customModal.style.display = 'flex';
                
                const input = modalBody.querySelector('input');
                if (input) {
                    input.focus();
                    input.select();
                }
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
                        const renameInput = document.getElementById('renameInput');
                        const newTitle = renameInput.value;
                        if (newTitle && newTitle.trim() !== "") {
                            chatSessions[sessionId].title = newTitle.trim();
                            renderChatHistory();
                        }
                    }
                });
            }

            function handleDelete(sessionId) {
                showModal({
                    title: 'Delete Chat',
                    body: `<p>Are you sure you want to delete this chat session?</p>`,
                    confirmText: 'Delete',
                    onConfirm: () => {
                        delete chatSessions[sessionId];
                        
                        if (currentSessionId === sessionId) {
                            const remainingSessions = Object.keys(chatSessions);
                            if (remainingSessions.length > 0) {
                                currentSessionId = remainingSessions[0];
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

            // --- Event Listeners ---
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
            });
            
            newChatBtn.addEventListener('click', () => {
                createNewSession();
            });


            profileIcon.addEventListener('click', function() {
                closeAllMenus();
                profilePopover.classList.toggle('show');
            });

            attachBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                closeAllMenus();
                attachPopover.classList.toggle('show');
            });

            window.addEventListener('click', function(e) {
                if (!profileIcon.contains(e.target) && !profilePopover.contains(e.target)) {
                    profilePopover.classList.remove('show');
                }
                
                if (!e.target.closest('.topic-menu-btn') && !e.target.closest('.topic-menu')) {
                     if(!e.target.closest('#attachBtn') && !e.target.closest('#attachPopover')) {
                        closeAllMenus();
                    }
                }
            });

            SignOut.addEventListener('click', function() {
                window.location.href = "index.html";
            });
            
            // Modal event listeners
            modalConfirmBtn.addEventListener('click', () => {
                if (modalConfirmCallback) {
                    modalConfirmCallback();
                }
                hideModal();
            });

            modalCancelBtn.addEventListener('click', hideModal);

            customModal.addEventListener('click', (e) => {
                if (e.target === customModal) {
                    hideModal();
                }
            });
            
            const API_BASE_URL = 'http://localhost:8000'; 
            
            function getModelRoute(modelValue) {
                switch (modelValue) {
                    case 'gemini':
                        return '/gemini_chat/invoke'; 
                    case 'llama':
                        return '/llama_chat/invoke'; 
                    case 'gemma':
                        return '/gemma_chat/invoke';
                    default:
                        // Fallback or error handling
                        console.error(`Unknown model selected: ${modelValue}`);
                        return '/gemini_chat/invoke'; 
                }
            }
            
            async function fetchAssistantResponse(userInput, selectedModel) {
                const routePath = getModelRoute(selectedModel);
                const fullUrl = API_BASE_URL + routePath;
                
                try {
                    // Start simulation response immediately for a better UX

                    const response = await fetch(fullUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        // LangServe routes for 'invoke' expect an 'input' object
                        body: JSON.stringify({ input: { questions: userInput } }),
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const jsonResponse = await response.json();
                    
                    const assistantContent = jsonResponse.output; 
                    addMessageToCurrentSession('assistant', assistantContent);

                } catch (error) {
                    console.error('Error fetching assistant response:', error);
                    // Handle API failure
                    addMessageToCurrentSession('assistant', "Oops! Ran into an issue talking to the model. Try again?");
                }
            }

            chatForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const userInput = chatInput.value.trim();
                const selectedModel = llmModelSelect.value; // Get the selected LLM model

                if (userInput && currentSessionId) {
                    addMessageToCurrentSession('user', userInput);
                    console.log(`Selected Model: ${selectedModel}, User Input: ${userInput}`);
                    
                    chatInput.value = '';
                    fetchAssistantResponse(userInput, selectedModel);
                }
            });

            chatInput.focus();
            // --- Initial Setup ---
            setupUser();
            createNewSession();
        });
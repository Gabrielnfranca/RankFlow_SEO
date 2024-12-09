document.addEventListener('DOMContentLoaded', function() {
    // Inicializar Sortable em todas as colunas
    document.querySelectorAll('.kanban-items').forEach(column => {
        new Sortable(column, {
            group: 'kanban',
            animation: 150,
            ghostClass: 'dragging',
            onEnd: function(evt) {
                const taskId = evt.item.dataset.taskId;
                const newStatus = evt.to.dataset.status;
                updateTaskStatus(taskId, newStatus);
            }
        });
    });

    // Função para atualizar o status da tarefa
    function updateTaskStatus(taskId, status) {
        fetch('/api/task/update-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                taskId: taskId,
                status: status
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateProgress();
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Atualizar progresso geral
    function updateProgress() {
        const totalTasks = document.querySelectorAll('.kanban-item').length;
        const completedTasks = document.querySelectorAll('#done .kanban-item').length;
        const progress = Math.round((completedTasks / totalTasks) * 100);
        
        const progressBar = document.querySelector('.progress-bar');
        progressBar.style.width = progress + '%';
        progressBar.setAttribute('aria-valuenow', progress);
        progressBar.textContent = progress + '%';
    }

    // Modal de Tarefa
    const taskModal = document.getElementById('taskModal');
    if (taskModal) {
        taskModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const taskId = button.dataset.taskId;
            loadTaskDetails(taskId);
        });
    }

    // Carregar detalhes da tarefa
    function loadTaskDetails(taskId) {
        fetch(`/api/task/${taskId}`)
            .then(response => response.json())
            .then(task => {
                document.getElementById('taskTitle').value = task.title;
                document.getElementById('taskDescription').value = task.description;
                document.getElementById('taskPriority').value = task.priority;
                
                // Carregar checklist
                const checklistContainer = document.getElementById('taskChecklist');
                checklistContainer.innerHTML = '';
                task.checklist.forEach((item, index) => {
                    addChecklistItem(item.text, item.completed);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    // Adicionar item ao checklist
    document.getElementById('addChecklistItem').addEventListener('click', function() {
        addChecklistItem();
    });

    function addChecklistItem(text = '', completed = false) {
        const checklistContainer = document.getElementById('taskChecklist');
        const itemDiv = document.createElement('div');
        itemDiv.className = 'checklist-item d-flex align-items-center gap-2 mb-2';
        itemDiv.innerHTML = `
            <input type="checkbox" class="form-check-input" ${completed ? 'checked' : ''}>
            <input type="text" class="form-control form-control-sm" value="${text}" placeholder="Item do checklist">
            <button type="button" class="btn btn-sm btn-outline-danger" onclick="this.parentElement.remove()">
                <i class="bi bi-trash"></i>
            </button>
        `;
        checklistContainer.appendChild(itemDiv);
    }

    // Salvar tarefa
    document.getElementById('saveTask').addEventListener('click', function() {
        const taskData = {
            title: document.getElementById('taskTitle').value,
            description: document.getElementById('taskDescription').value,
            priority: document.getElementById('taskPriority').value,
            checklist: Array.from(document.querySelectorAll('.checklist-item')).map(item => ({
                text: item.querySelector('input[type="text"]').value,
                completed: item.querySelector('input[type="checkbox"]').checked
            }))
        };

        fetch('/api/task/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const modal = bootstrap.Modal.getInstance(taskModal);
                modal.hide();
                location.reload(); // Recarregar para mostrar as mudanças
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Exportar progresso
    document.getElementById('exportProgress').addEventListener('click', function() {
        fetch('/api/export-progress')
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'seo-tecnico-progress.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
            })
            .catch(error => console.error('Error:', error));
    });

    // Filtros
    document.getElementById('applyFilters').addEventListener('click', function() {
        const filters = {
            priority: {
                high: document.getElementById('filterHigh').checked,
                medium: document.getElementById('filterMedium').checked,
                low: document.getElementById('filterLow').checked
            },
            date: document.getElementById('filterDate').value
        };

        fetch('/api/tasks/filter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(filters)
        })
        .then(response => response.json())
        .then(data => {
            // Atualizar o Kanban com as tarefas filtradas
            updateKanbanBoard(data);
            const modal = bootstrap.Modal.getInstance(document.getElementById('filterModal'));
            modal.hide();
        })
        .catch(error => console.error('Error:', error));
    });
});

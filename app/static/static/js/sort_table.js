document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('th.sortable').forEach(header => {
        header.addEventListener('click', function() {
            const table = header.closest('table');
            const tbody = table.querySelector('tbody');
            const index = Array.prototype.indexOf.call(header.parentElement.children, header);
            const order = header.classList.contains('asc') ? 'desc' : 'asc';

            Array.from(table.querySelectorAll('th')).forEach(th => th.classList.remove('asc', 'desc'));
            header.classList.add(order);

            const rows = Array.from(tbody.querySelectorAll('tr')).sort((rowA, rowB) => {
                const cellA = rowA.children[index].innerText;
                const cellB = rowB.children[index].innerText;
                
                if (index === 4) { // Score column
                    const scoreA = cellA === 'No score' ? -1 : parseInt(cellA, 10);
                    const scoreB = cellB === 'No score' ? -1 : parseInt(cellB, 10);
                    return order === 'asc' ? scoreA - scoreB : scoreB - scoreA;
                }

                return order === 'asc' 
                    ? cellA.localeCompare(cellB, undefined, {numeric: true})
                    : cellB.localeCompare(cellA, undefined, {numeric: true});
            });

            rows.forEach(row => tbody.appendChild(row));
        });
    });
});

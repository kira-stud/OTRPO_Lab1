    function searchPokemons(page, searchValue) {
        fetch(`/search?search=${searchValue}&page=${page}`)
            .then(response => response.json())
            .then(data => {
                updateTable(data[0]);
                updatePagination(data[1], data[2], searchValue);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    function updateTable(data) {
        var tableHTML = '<thead><th>Картинка</th><th>Описание</th></thead><tbody class="myTable">';
        for (var i = 0; i < data.length; i++) {
            tableHTML += `<tr onclick="location.href='/${data[i].name}'"><td><img src="${data[i].image}"></td><td>`;
            tableHTML += '<div class="fs-4">' + data[i].name + '</div><br>';
            tableHTML += '<div>Атака: ' + data[i].attack + '</div>';
            tableHTML += '<div>Здоровье: ' + data[i].hp + '</div>';
            tableHTML += '</td></tr>';
        }
        tableHTML += '</tbody>';

        document.querySelector('.table').innerHTML = tableHTML;
    }

    function updatePagination(cur, last, searchValue) {
        var navHTML = ''
        if (cur === 1)
            navHTML += '<li class="page-item disabled">'
        else
            navHTML += '<li class="page-item">'
        navHTML += `<button class="page-link" tabindex="-1" onclick="searchPokemons(${cur - 1}, '${searchValue}')">Назад</button></li>`
        navHTML += '<li class="page-item"><p class="page-link">' + cur + '<span class="sr-only"></span></p></li>'
        if (cur === last)
            navHTML += '<li class="page-item disabled">'
        else
            navHTML += '<li class="page-item">'
        navHTML += `<button class="page-link" onclick="searchPokemons(${cur + 1}, '${searchValue}')">Вперёд</button></li>`
        document.querySelector('.pagination').innerHTML = navHTML;
    }
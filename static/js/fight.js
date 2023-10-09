    function fightValues(player_value) {
        console.log("UHU")
        if (player_value === "" || player_value < 1 || player_value > 10)
            return
        fetch(`/attack?val=${player_value}`)
            .then(response => response.json())
            .then(data => {
                values = document.querySelector('.values').innerHTML;
                values += `<p>${player_value} vs ${data['bot_val']}</p>`;
                document.querySelector('.values').innerHTML = values;

                document.getElementById("player_hp").value = Math.max(data['hp'], 0);
                document.getElementById("bot_hp").value = Math.max(data['bot_hp'], 0);
                document.getElementById("player_attack").value = data['attack'];
                document.getElementById("bot_attack").value = data['bot_attack'];

                if (data['bot_hp'] <= 0 || data['hp'] <= 0){
                    var button = document.getElementById("attack");
                    button.textContent = "На главную";
                    button.removeAttribute("onclick");
                    button.addEventListener('click', function (e) {
                        location.href="/"})
                    if (data['hp'] <= 0)
                        document.querySelector('.values').innerHTML = values + `<p class="fs-5">ТЫ ПРОИГРАЛ</p>`;
                    else
                        document.querySelector('.values').innerHTML = values + `<p class="fs-5">ТЫ ВЫИГРАЛ</p>`;
                    }
            })
    }

    function enforceMinMax(el) {
      if (el.value != "") {
        if (parseInt(el.value) < parseInt(el.min)) {
          el.value = el.min;
        }
        if (parseInt(el.value) > parseInt(el.max)) {
          el.value = el.max;
        }
      }
      else
        el.value = 1
    }
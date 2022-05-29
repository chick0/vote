function render_display(){
    const display = document.getElementById("display");
    display.innerHTML = "";

    const handler = (event) => {
        const target = event.target;
        Swal.fire({
            icon: "question",
            text: "해당 선택지를 삭제하시겠습니까?",
            showCancelButton: true,
            showConfirmButton: true,
            confirmButtonText: "네",
            cancelButtonText: "아니요",
        }).then((result) => {
            if(result.isConfirmed){
                fetch(`/api/opt?vote_id=${vote_id}&option_id=${target.dataset.id}`, {
                    method: "DELETE",
                }).then((resp) => resp.json()).then((json) => {
                    if(json.code == 200){
                        delete opts[target.dataset.id];
                        render_display();
                    } else {
                        Swal.fire({
                            icon: "error",
                            text: json.message,
                            showCancelButton: false,
                            showConfirmButton: true,
                            confirmButtonText: "닫기",
                            timer: 2022,
                            timerProgressBar: true
                        });
                    }
                });
            }
        });
    };

    Object.keys(opts).forEach((id) => {
        const box = document.createElement("box");
        box.setAttribute("data-id", id);
        box.setAttribute("class", "box");
        box.setAttribute("style", "font-size:1.5rem;");
        box.appendChild(document.createTextNode(opts[id]));
        box.addEventListener("click", handler);
        display.appendChild(box);
    });
}

function create_option(name) {
    fetch(`/api/opt?vote_id=${vote_id}`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name
        })
    }).then((resp) => resp.json()).then((json) => {
        if(json.code == 201){
            Swal.fire({
                icon: "success",
                text: json.message,
                showCancelButton: false,
                showConfirmButton: true,
                confirmButtonText: "닫기",
                timer: 2022,
                timerProgressBar: true
            });

            opts[json.data.option_id] = name;
            render_display();
        } else {
            Swal.fire({
                icon: "info",
                text: json.message,
                showCancelButton: false,
                showConfirmButton: true,
                confirmButtonText: "닫기",
                timer: 2022,
                timerProgressBar: true
            });
        }
    });
}
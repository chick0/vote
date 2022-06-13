function render_display(){
    const display = document.getElementById("display");
    display.innerHTML = "";

    function delete_handler(event){
        const option_id = event.target.dataset.id;
        Swal.fire({
            icon: "question",
            text: "해당 선택지를 삭제하시겠습니까?",
            showCancelButton: true,
            showConfirmButton: true,
            confirmButtonText: "네",
            cancelButtonText: "아니요",
        }).then((result) => {
            if(result.isConfirmed){
                fetch(`/api/opt?vote_id=${vote_id}&option_id=${option_id}`, {
                    method: "DELETE",
                }).then((resp) => resp.json()).then((json) => {
                    if(json.code == 200){
                        delete opts[option_id];
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

        const option = document.createElement("p");
        option.setAttribute("class", "mb-2");
        option.appendChild(document.createTextNode(opts[id]));
        box.appendChild(option);

        const button = document.createElement("button");
        button.setAttribute("data-id", id);
        button.setAttribute("class", "button is-danger");
        button.appendChild(document.createTextNode("선택지 삭제"));
        button.addEventListener("click", delete_handler);
        box.appendChild(button);

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
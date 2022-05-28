function render_display(){
    function err(message) {
        Swal.fire({
            icon: "error",
            text: message,
            showCancelButton: false,
            showConfirmButton: true,
            confirmButtonText: "닫기",
            timer: 2022,
            timerProgressBar: true
        });
    }

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
                axios({
                    method: "DELETE",
                    url: "/api/opt",
                    params: {
                        vote_id: vote_id,
                        option_id: target.dataset.id,
                    },
                }).then(() => {
                    delete opts[target.dataset.id]
                    render_display();
                }).catch((error) => {
                    const resp = error.response;
                    if(resp == undefined){
                        err("알 수 없는 오류가 발생했습니다.");
                    } else {
                        err(resp.data.message);
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
    function err(message) {
        Swal.fire({
            icon: "error",
            text: message,
            showCancelButton: false,
            showConfirmButton: true,
            confirmButtonText: "닫기",
            timer: 2022,
            timerProgressBar: true
        });
    }

    axios({
        method: "POST",
        url: "/api/opt",
        params: {
            vote_id: vote_id,
        },
        data: {
            name: name
        }
    }).then((resp) => {
        const data = resp.data;
        opts[data.data.option_id] = name;
        render_display();

        Swal.fire({
            icon: "info",
            text: data.message,
            showCancelButton: false,
            showConfirmButton: true,
            confirmButtonText: "닫기",
            timer: 2022,
            timerProgressBar: true
        });
    }).catch((error) => {
        const resp = error.response;
        if(resp == undefined){
            err("알 수 없는 오류가 발생했습니다.");
        } else {
            err(resp.data.message);
        }
    });
}
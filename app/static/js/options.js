function render_display(){
    const display = document.getElementById("display");
    display.innerHTML = "";

    Object.keys(opts).forEach((id) => {
        const li = document.createElement("li");
        li.appendChild(document.createTextNode(opts[id]));
        li.setAttribute("data-opt-id", id);

        display.appendChild(li);
    });
}

function create_option(name) {
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
        window.alert(data.message);

        render_display();
    }).catch((err) => {
        const resp = err.response;
        if(resp == undefined){
            window.alert("알 수 없는 오류가 발생했습니다.");
        } else {
            const data = resp.data;
            window.alert(data.message);
        }
    });
}

function delete_option(option_id) {
    // send req to api
    // return result
}
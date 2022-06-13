function update_status() {
    fetch(`/api/count?vote_id=${vote_id}`).then((resp) => resp.json()).then((json) => {
        document.getElementById("total").innerText = json.data.total;
        document.getElementById("selected").innerText = json.data.selected;
        document.getElementById("per").innerText = parseInt(json.data.selected / json.data.max * 100);

        if(json.data.selected == json.data.max) {
            Swal.fire({
                icon: "success",
                text: "투표가 마감되었습니다!",
                showCancelButton: false,
                showConfirmButton: true,
                confirmButtonText: "닫기",
                timer: 3500,
                timerProgressBar: true
            }).then(() => {
                location.href = result_url;
            });
        }
    });
}

function start_vote(){
    fetch(`/vote/panel/${vote_id}`, {
        method: "POST"
    }).then((resp) => resp.json()).then((json) => {
        if(json.code == 200){
            // hide start button
            document.getElementById("vote_start").classList.add("is-hidden");
            // show end button
            document.getElementById("vote_end").classList.remove("is-hidden");

            Swal.fire({
                icon: "success",
                text: json.message,
                showCancelButton: false,
                showConfirmButton: true,
                confirmButtonText: "닫기",
                timer: 2022,
                timerProgressBar: true
            });
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

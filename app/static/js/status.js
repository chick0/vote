function update_status() {
    axios({
        method: "GET",
        url: "/api/count",
        params: {
            vote_id: vote_id,
        },
    }).then((resp) => {
        const data = resp.data;
        document.getElementById("total").innerText = data.data.total;
        document.getElementById("selected").innerText = data.data.selected;
        document.getElementById("per").innerText = parseInt(data.data.selected / data.data.max * 100);

        if(data.data.selected == data.data.max) {
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
    }).catch((err) => {
        console.error(err);
    })
}

function start_vote(){
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
        url: `/vote/panel/${vote_id}`,
    }).then((resp) => {
        // hide start button
        document.getElementById("vote_start").classList.add("is-hidden");
        // show end button
        document.getElementById("vote_end").classList.remove("is-hidden");

        Swal.fire({
            icon: "success",
            text: resp.data.message,
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

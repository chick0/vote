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
    }).catch((err) => {
        console.error(err);
    })
}

function start_vote(){
    axios({
        method: "POST",
        url: `/vote/panel/${vote_id}`,
    }).then((resp) => {
        const data = resp.data;
        window.alert(data.message);
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

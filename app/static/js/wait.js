function update_status(){
    axios({
        method: "GET",
        url: "/api/vote",
        params: {
            vote_id: vote_id,
        },
    }).then((resp) => {
        const data = resp.data;
        if(data.data.status) {
            location.reload();
        }
    }).catch((err) => {
        console.error(err);
    });
}
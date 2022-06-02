function update_status(){
    fetch(`/api/vote?vote_id=${vote_id}`).then((resp) => resp.json()).then((json) => {
        if(json.message.length != 0){
            clearInterval(work_id);
            window.alert(json.message);
        }

        if(json.data.status === true) {
            location.reload();
        }
    });
}

function watch_restart(){
    fetch(`/api/vote?vote_id=${vote_id}`).then((resp) => resp.json()).then((json) => {
        if(json.message.length != 0){
            clearInterval(work_id);
            window.alert(json.message);
        }

        if(json.data.status === false) {
            location.reload();
        }
    });
}
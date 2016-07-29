/**
 * Created by roddac on 28/07/2016.
 */

$(".btn-update-users").click(function(){
    $.post("/ui/",
            {
                user_update: 'true'
            },
    function(data,status){
        for(i=0; i<data.result.length; i++) {
            console.log(data.result[i]);
            // Got the data now generate the table format
        }
    });
});
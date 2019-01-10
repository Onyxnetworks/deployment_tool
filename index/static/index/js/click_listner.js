function clicklisten() {
    $(".navbar").click(function (event) {
        event.preventDefault();
        console.log('Test');
    });
}
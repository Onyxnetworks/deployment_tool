function clicklisten_disable() {
    $(".navbar").click(function () {
        console.log('Link Clicked');
        return false;
    });
}

function clicklisten_enable() {
    $(".navbar").click(function () {
        console.log('Link Clicked Enable');
        return true;
    });
}
$(document).ready(function () {

    $("#asidebard_btn").click(function () {

        if (!$("#asidenav").hasClass("open_aside")) {
            $("#asidenav").addClass("open_aside");
            $(".content_body").css("margin-left", "0px");
            $(".list_ul_drop>li").addClass("col-xs-6 col-md-3 col-lg-2 col-6");
            $(".content_body").css("display", "block");
        } else {

            $(".list_ul_drop>li").removeClass();
            $("#asidenav").removeClass("open_aside");
            $(".content_body").css("margin-left", "230px");

            if ($(window).width() < 747) {
                $(".content_body").css("display", "flex");
            }
        }

    })



    if ($(window).width() < 747) {


        $("#asidenav").addClass("open_aside");
        $(".content_body").css("margin-left", "0px");
        // $(".content_body").css("display", "flex");
        $(".list_ul_drop>li").addClass("col-xs-6 col-md-3 col-lg-2 col-6");
    }


    $(".listnav>li>a").mouseenter(function () {
        var classs = $(this).find("i").attr("class");

        $(this).find("i").css("padding-left", "3px");
        $(this).find("i").css("margin-right", "5px");

        if (!$(this).hasClass("activepage")) {
            $(this).addClass("activepage");
        }


    })

    $(".listnav>li>a").mouseleave(function () {
        if ($(this).attr("rel") != "active") {
            $(this).removeClass("activepage");
        } else {
            $(this).find("a").css("padding-left", "3px");
            $(this).find("a").css("margin-right", "5px");
        }

        $(this).find("i").css("padding-left", "8px");
        $(this).find("i").css("margin-right", "10px");
    })

    $(".listnav>li>a").click(function () {

        var dropdown = $(this).attr("data-show");
        $(".submenus").slideUp(450);

        $(this).attr("rel", "");
        $(this).removeClass("rel", "activepage");

        var avaible_active = $(".activepage").length;

        $(".activepage").each(function () {
            $(this).removeClass("activepage");
            $(this).attr("rel", "");
        })

        if ($("#" + dropdown).css("display") == "block") {
            $("#" + dropdown).hide(450);
        } else {
            $("#" + dropdown).slideToggle(450);

        }

        $(this).addClass("activepage");
        $(this).attr("rel", "active");
    })

    $(".hide_seekerlist_drop").click(function () {
        var item_control = $(this).attr("data-widget");
        $("#" + item_control).slideToggle()
    })

    $(".remove_seekerlist_drop").click(function () {
        var item_control = $(this).attr("data-widget");
        $("#" + item_control).remove()
    })

    if ($("#asidenav").hasClass("open_aside")) {
        $(".content_body").css("display", "block");
    }

    $("#checkall").click(function () {
        $(".check_select").prop("checked", function (i, oldVal) {

            return !oldVal;
        });
    })


    $(".hide_seekerlist_drop").click(function () {
        var item_control = $(this).attr("data-widget");
        $("#" + item_control).slideToggle()
    })

    $(".remove_seekerlist_drop").click(function () {
        var item_control = $(this).attr("data-widget");
        $("#" + item_control).remove()
    })

    
    $("#close_activetopaid").click(function () {
        $(".active_to_paid_wrapper").hide();
    })

    $("#activetopaidbtn").click(function () {
        $(".active_to_paid_wrapper").show();
    })

})


function checkAll(ele) {
    var checkingElement = $('input[name="check_all"]');

    if (ele.checked) {
        for (var i = 0; i < checkingElement.length; i++) {
            if (checkingElement[i].type == 'checkbox') {
                checkingElement[i].checked = true;
            }
        }
    } else {
        for (var i = 0; i < checkingElement.length; i++) {
            console.log(i)
            if (checkingElement[i].type == 'checkbox') {
                checkingElement[i].checked = false;
            }
        }
    }
}


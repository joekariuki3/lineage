// $(".member").click(function () {
//   let id = $(this).attr("member1_id");
//   let myData = JSON.stringify({ member1_id: id });
//   let url = "/member/nuclear";
//   $.ajax({
//     url: url,
//     type: "POST",
//     data: myData,
//     dataType: "json",
//     contentType: "application/json",
//     success: function (resp) {
//       const spouses = resp.spouses;
//       const children = resp.children;
//       $.each(spouses, function (index, spouse) {
//         $(`#spouse_${id}`).append(`<h4>${spouse.first_name}</h4>`);
//       });
//       $.each(children, function (index, child) {
//         $(`#children_${id}`).append(`
//         <details>
//             <summary class="member" member1_id="${child.member_id}" onclick="getNuclear(event)">
//                 ${child.first_name} ${child.last_name} |
//                 <a href="/member/${child.member_id}">Add Member </a>
//              </summary>
//              <div class="" id="spouse_${child.member_id}"></div>
//              <div class="" id="children_${child.member_id}"></div>
//         </details>`);
//       });
//     },
//   });
// });

function getNuclear(event) {
  let id = event.target.getAttribute("member1_id");
  let detailIsOpen = event.target.parentElement.hasAttribute("open");
  let myData = JSON.stringify({ member1_id: id });
  let url = "/member/nuclear";
  if (detailIsOpen) {
    $(`#spouse_${id}`).empty();
    $(`#children_${id}`).empty();
  } else {
    $.ajax({
      url: url,
      type: "POST",
      data: myData,
      dataType: "json",
      contentType: "application/json",
      success: function (resp) {
        const spouses = resp.spouses;
        const children = resp.children;
        $.each(spouses, function (index, spouse) {
          $(`#spouse_${id}`).append(`<h4>${spouse.first_name}</h4>`);
        });
        $.each(children, function (index, child) {
          $(`#children_${id}`).append(`
            <details>
                <summary class="member" member1_id="${child.member_id}" onclick="getNuclear(event)">
                    ${child.first_name} ${child.last_name} |
                    <a href="/member/${child.member_id}">Add Member </a>
                 </summary>
                 <div class="" id="spouse_${child.member_id}"></div>
                 <div class="" id="children_${child.member_id}"></div>
            </details>`);
        });
      },
    });
  }
}

function getSpouse(event) {
  let id = event.target.getAttribute("member1_id");
  let detailIsOpen = event.target.parentElement.hasAttribute("open");
  let myData = JSON.stringify({ member1_id: id });
  let url = "/member/spouses";
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
        const spouses = resp;
        $.each(spouses, function (index, spouse) {
          let spouseClass = "";
          let alive = "";
          if (spouse.gender == "Female") {
            spouseClass = "wife";
          } else if (spouse.gender == "Male") {
            spouseClass = "husband";
          }
          if (!spouse.alive) {
            alive = "deceased";
          }

          $(`#spouse_${id}`).append(
            `<ul>
              <li>
                <details>
                  <summary class="member ${spouseClass} ${alive}" member1_id="${id}" spouse_id="${spouse.member_id}" onclick="getChildren(event)">
                    ${spouse.first_name} ${spouse.last_name}
                    </summary>
                    <div class="memeber-buttons">
                      <a href="/member/${id}/${spouse.member_id}/child" class="btn btn-light btn-sm">+ Child</a> |
                      <a href="/member/${spouse.member_id}">More...</a>
                    </div>
                  <div class="" id="children_${spouse.member_id}"></div>
                </details>
              </li>
            </ul>
            `
          );
        });
      },
    });
  }
}

function getChildren(event) {
  let id = event.target.getAttribute("member1_id");
  let s_id = event.target.getAttribute("spouse_id");
  let detailIsOpen = event.target.parentElement.hasAttribute("open");
  let myData = JSON.stringify({ member1_id: id, spouse_id: s_id });
  let url = "/member/children";
  if (detailIsOpen) {
    $(`#spouse_${s_id}`).empty();
    $(`#children_${s_id}`).empty();
  } else {
    $.ajax({
      url: url,
      type: "POST",
      data: myData,
      dataType: "json",
      contentType: "application/json",
      success: function (resp) {
        const children = resp;
        $.each(children, function (index, child) {
          let alive = "";
          if (!child.alive) {
            alive = "deceased";
          }
          $(`#children_${s_id}`).append(
            `<ul>
                <li>
                  <details>
                    <summary class="member ${alive}" member1_id="${child.member_id}" onclick="getSpouse(event)">
                      ${child.first_name} ${child.last_name}
                    </summary>
                    <div class="memeber-buttons">
                      <a href="/member/${child.member_id}/spouse" class="btn btn-light btn-sm">+ spouse</a> |
                      <a href="/member/${child.member_id}">More...</a>
                    </div>
                    <div class="" id="spouse_${child.member_id}"></div>
                  </details>
                </li>
              </ul>
            `
          );
        });
      },
      fail: function (xhr, textStatus, errorThrown) {
        console.log(xhr);
        console.log(textStatus);
        console.log(errorThrown);
      },
    });
  }
}

$(".alive li input").on("change", function () {
  if ($(this).val() === "False") {
    // remove hide class to show deathdate meaning person is not alive
    $(".deathdate").removeClass("hide");
  } else {
    $(".deathdate").addClass("hide");
  }
});

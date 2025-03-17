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
        const spouses = resp[0];
        const login = resp[1]["authenticated"];
        let addBtn = "";
        $.each(spouses, function (index, spouse) {
          let spouseClass = "";
          let alive = "";
          if (spouse.gender === "Female") {
            spouseClass = "wife";
          } else if (spouse.gender === "Male") {
            spouseClass = "husband";
          }
          if (!spouse.alive) {
            alive = "deceased";
          }

          if (login) {
            addBtn = `<a href="/member/${id}/${spouse.member_id}/child" class="btn btn-light btn-sm">+ Child</a> |`;
            console.log("logedin");
          }

          $(`#spouse_${id}`).append(
            `<ul>
              <li>
                <details>
                  <summary class="member ${spouseClass} ${alive}" member1_id="${id}" spouse_id="${spouse.member_id}" onclick="getChildren(event)">
                    ${spouse.first_name} ${spouse.last_name}
                    </summary>
                    <div class="member-buttons">
                     ${addBtn}
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
        const children = resp[0];
        const login = resp[1]["authenticated"];
        let addBtn = "";
        $.each(children, function (index, child) {
          let alive = "";
          if (login) {
            addBtn = `<a href="/member/${child.member_id}/spouse" class="btn btn-light btn-sm">+ spouse</a> |`;
            console.log("logedin");
          }
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
                    <div class="member-buttons">
                      ${addBtn}
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

// Function to copy a family link
function copyLink(linkId) {
  const copyText = document.getElementById("link_" + linkId);
  const copyButton = document.getElementById("copyBtn_" + linkId);

  // Select the link text
  copyText.select();
  document.execCommand("copy");

  // Change the button text to "Copied!"
  copyButton.innerHTML = '<i class="fa fa-check"></i> Copied!';
  copyButton.classList.add("bg-green-600");
  copyButton.classList.remove("bg-blue-600");

  // Revert back to the original text after 2 seconds
  setTimeout(function () {
    copyButton.innerHTML = '<i class="fa fa-clone"></i> Copy Link';
    copyButton.classList.add("bg-blue-600");
    copyButton.classList.remove("bg-green-600");
  }, 2000);
}

function toggleMemberMenu(event) {
  event.stopPropagation();
  event.preventDefault();
  const btn = event.currentTarget;
  const menu = btn.nextElementSibling;

  // Close any other open member dropdowns
  document.querySelectorAll(".member-dropdown-menu").forEach((m) => {
    if (m !== menu) {
      m.classList.add("hidden");
    }
  });

  const isOpening = menu.classList.contains("hidden");
  menu.classList.toggle("hidden");

  if (isOpening) {
    // Reset to default left alignment
    menu.style.left = "0";
    menu.style.right = "auto";

    // If the dropdown extends beyond the right edge of the viewport, anchor to the right
    const rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth - 8) {
      menu.style.left = "auto";
      menu.style.right = "0";
    }
  }
}

// Close member dropdown menus when clicking outside
$(document).on("click", function (e) {
  if (!$(e.target).closest(".member-dropdown").length) {
    $(".member-dropdown-menu").addClass("hidden");
  }
});

function getSpouse(event) {
  let memberEl = event.currentTarget || event.target.closest(".member");
  if (!memberEl) return;
  let id = memberEl.getAttribute("member1_id");
  let detailIsOpen = memberEl.closest("details").hasAttribute("open");
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
            addBtn = `<a href="/member/${id}/${spouse.member_id}/child" class="member-dropdown-item"><span class="item-icon text-green-600">+</span><span>Add Child</span></a>`;
          }

          $(`#spouse_${id}`).append(
            `<ul>
              <li>
                <details>
                  <summary class="member ${spouseClass} ${alive}" member1_id="${id}" spouse_id="${spouse.member_id}" onclick="getChildren(event)">
                    <span class="member-name">${spouse.first_name} ${spouse.last_name}</span>
                    <span class="member-actions" onclick="event.stopPropagation()">
                      <div class="member-dropdown">
                        <button type="button" class="member-menu-btn" onclick="toggleMemberMenu(event)" title="Options" aria-label="Options">
                          <svg class="menu-dots-icon" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16 12a2 2 0 100-4 2 2 0 000 4z"></path>
                          </svg>
                        </button>
                        <div class="member-dropdown-menu hidden">
                          ${addBtn}
                          <a href="/member/${spouse.member_id}" class="member-dropdown-item">
                            <span class="item-icon text-blue-500">👤</span>
                            <span>Profile</span>
                          </a>
                        </div>
                      </div>
                    </span>
                  </summary>
                  <div class="" id="children_${spouse.member_id}"></div>
                </details>
              </li>
            </ul>
            `,
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

function getChildren(event) {
  let memberEl = event.currentTarget || event.target.closest(".member");
  if (!memberEl) return;
  let id = memberEl.getAttribute("member1_id");
  let s_id = memberEl.getAttribute("spouse_id");
  let detailIsOpen = memberEl.closest("details").hasAttribute("open");
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
        if (children.length === 0) {
          $(`#children_${s_id}`).append(
            `<ul>
              <li>
                <details>
                  <summary class="member" member1_id="${id}" spouse_id="${s_id}">
                    <span class="member-name text-gray-500 italic">No children Yet</span>
                  </summary>
                </details>
              </li>
            </ul>`,
          );
        }
        $.each(children, function (index, child) {
          let alive = "";
          if (login) {
            addBtn = `<a href="/member/${child.member_id}/spouse" class="member-dropdown-item"><span class="item-icon text-green-600">+</span><span>Add Spouse</span></a>`;
          }
          if (!child.alive) {
            alive = "deceased";
          }
          $(`#children_${s_id}`).append(
            `<ul>
                <li>
                  <details>
                    <summary class="member ${alive}" member1_id="${child.member_id}" onclick="getSpouse(event)">
                      <span class="member-name">${child.first_name} ${child.last_name}</span>
                      <span class="member-actions" onclick="event.stopPropagation()">
                        <div class="member-dropdown">
                          <button type="button" class="member-menu-btn" onclick="toggleMemberMenu(event)" title="Options" aria-label="Options">
                            <svg class="menu-dots-icon" viewBox="0 0 20 20" fill="currentColor">
                              <path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16 12a2 2 0 100-4 2 2 0 000 4z"></path>
                            </svg>
                          </button>
                          <div class="member-dropdown-menu hidden">
                            ${addBtn}
                            <a href="/member/${child.member_id}" class="member-dropdown-item">
                              <span class="item-icon text-blue-500">👤</span>
                              <span>Profile</span>
                            </a>
                          </div>
                        </div>
                      </span>
                    </summary>
                    <div class="" id="spouse_${child.member_id}"></div>
                  </details>
                </li>
              </ul>
            `,
          );
        });
      },
      error: function (xhr, textStatus, errorThrown) {
        console.log(xhr);
        console.log(xhr.status);
        console.log(textStatus);
        console.log(errorThrown);
      },
    });
  }
}

$(".alive li input").on("change", function () {
  if ($(this).val() === "False") {
    // remove hide class to show deathdate meaning person is not alive
    $(".deathdate").removeClass("hidden");
  } else {
    $(".deathdate").addClass("hidden");
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

// On Error page, get Home button and redirect to home page
const homeButton = document.getElementById("homeButton");
if (homeButton) {
  homeButton.addEventListener("click", function () {
    window.location.href = "/";
  });
}

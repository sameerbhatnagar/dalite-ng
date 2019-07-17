import { buildReq } from "../_ajax/utils.js";

let model;

function initModel(followerUrl)
{
  model = {

    urls: {
        followerUrl:followerUrl
    }
  }
}
export function init(followerUrl){

  addEventListener();
  initModel(followerUrl);

}
function addEventListener()
{
  document.querySelectorAll(".follower-button").forEach(element => element.addEventListener("click", toggleFollower));


}
function toggleFollower(event){
  const button = event.currentTarget;
  const pk = button.getAttribute("data-collection-pk");
  const req = buildReq({pk:pk}, "post");
  fetch(model.urls.followerUrl, req).then(resp => {if (resp.ok) {
    toggleFollowerView(
      button
    )
  } else {
    console.log(resp);
  }});

}
function toggleFollowerView(button){
  if(button.classList.contains("follower-button--following"))
  {
    button.classList.remove("follower-button--following");
  }
  else {
    button.classList.add("follower-button--following");
  }
}

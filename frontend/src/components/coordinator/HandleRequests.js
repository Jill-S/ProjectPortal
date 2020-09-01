import React from "react";
import { Link } from "react-router-dom";
import "./HandleRequests.scss";
import axios from "../../axios";
import Loading from "../shared/Loading";

class HandleRequests extends React.Component {
  constructor() {
    super();
    this.state = {
      view: "All",
      status: "",
      loading: true,
    };
    this.project_requests = [];
    this.group_requests = [];
  }
  componentDidMount() {
    axios
      .get("coordinatorGroupRequest/")
      .then(({ data }) => {
        this.group_requests = data.group_requests;
        console.log(this.group_requests);
        this.setState({ loading: false });
      })
      .catch((err) => this.props.history.goBack());

    axios
      .get("coordinatorProjectRequest/")
      .then(({ data }) => {
        this.project_requests = data.project_requests;
        console.log(this.project_requests);
        this.setState({ loading: false });
      })
      .catch((err) => this.props.history.goBack());
  }

  render() {
    if (this.state.loading) return <Loading />;
    return (
      <div className="handle-requests mx-auto" style={{ width: "90%" }}>
        <br />
        <div
          className="p-2 px-3 text-center shadow-sm rounded font-weight-bold"
          style={{
            color: "rgb(183, 32, 46)",
            fontSize: "1.1em",
            backgroundColor: "rgba(231, 231, 231, 0.459)",
          }}
        >
          Handle Requests
        </div>
        <br />

        {console.log("Group reqs", this.group_requests)}
        <div class="form-group">
          <label for="sel1">Select type of requests</label>
          <select
            class="form-control"
            id="sel1"
            onChange={() => {
              this.setState({ view: document.getElementById("sel1").value });
            }}
          >
            <option selected>All</option>
            <option>Group</option>
            <option>Project</option>
          </select>
        </div>
        {this.group_requests &&
          (this.state.view === "Group" || this.state.view === "All") &&
          this.group_requests.map((req) => {
            if (req.status === "Pending") {
              return (
                <div className="col-12 my-2 shadow-sm p-0">
                  <div
                    className="bg-light font-weight-bold p-2"
                    style={{ color: "rgb(183, 32, 46)", fontSize: "1em" }}
                  >
                    {req.action}
                  </div>

                  <div
                    className="d-flex flex-md-row flex-column px-2 py-1 text-muted"
                    style={{ fontSize: "0.9em" }}
                  >
                    <div className="col-md-6 col-12  p-0">
                      Group Number : {req.team}
                    </div>
                    <div className="col-md-6 col-12 p-0 pt-1">
                      {req.action === "Change Leader" && (
                        <span>Current Leader: {req.old_leader}</span>
                      )}
                      {req.action === "Removal of a student from group" && (
                        <span>Student to be removed: {req.remove_student}</span>
                      )}
                      {req.action === "Addition of a student to a group" && (
                        <span>Student to be added: {req.add_student}</span>
                      )}
                    </div>
                  </div>

                  {req.action === "Change Leader" && (
                    <div
                      className="px-2 text-muted py-1"
                      style={{ fontSize: "0.9em" }}
                    >
                      New Leader : {req.new_leader}
                    </div>
                  )}
                  {req.action !== "Change Leader" && (
                    <div
                      className="px-2 text-muted py-1"
                      style={{ fontSize: "0.9em" }}
                    >
                      Description : {req.description}
                    </div>
                  )}
                  <div className="d-flex flex-md-row flex-column py-1">
                    <div className="d-flex flex-row px-2 col-md-6 col-12">
                      <div className="pr-1">
                        <button
                          className="btn btn-outline-success"
                          onClick={() => {
                            axios
                              .put(`coordinatorGroupRequestManage/${req.id}/A`)
                              .then(() => window.location.reload())
                              .catch((err) => console.log(err));
                            this.setState({ status: "A" });
                          }}
                        >
                          Accept
                        </button>
                      </div>
                      <div className="pl-1">
                        <button
                          className="btn btn-outline-danger "
                          onClick={() => {
                            axios
                              .put(`coordinatorGroupRequestManage/${req.id}/R`)
                              .then(() => window.location.reload())
                              .catch((err) => console.log(err));
                            this.setState({ status: "R" });
                          }}
                        >
                          Reject
                        </button>
                      </div>
                    </div>
                    <div className="col-md-6 col-12 d-flex link  align-items-center py-2">
                      <Link to={`/group/${req.team}`}>
                        <div className="text-primary">View Group Details</div>
                      </Link>
                    </div>
                  </div>
                </div>
              );
            } else {
              return null;
            }
          })}

        {this.project_requests &&
          (this.state.view === "Project" || this.state.view === "All") &&
          this.project_requests.map((req) => {
            if (req.status === "P") {
              return (
                <div className="col-12 my-2 shadow-sm p-0">
                  <div
                    className="bg-light font-weight-bold p-2"
                    style={{ color: "rgb(183, 32, 46)", fontSize: "1em" }}
                  >
                    Project Approval Request
                  </div>

                  <div
                    className="d-flex flex-md-row flex-column px-2 py-1 text-muted"
                    style={{ fontSize: "0.9em" }}
                  >
                    <div className="col-md-6 col-12  p-0">
                      {" "}
                      Project Id: {req.project}
                    </div>
                    <div className="col-md-6 col-12 p-0 pt-1">
                      Request Id :{req.id}
                    </div>
                  </div>

                  <div
                    hidden
                    className="px-2 text-muted py-1 text-wrap"
                    style={{ fontSize: "0.9em", wordBreak: "break-word" }}
                  >
                    Request Description : {req.description}
                  </div>
                  <div className="d-flex flex-md-row  flex-column py-1">
                    <div className="col-md-6 col-12 bg- m-0 p-2">
                      {/* <form onSubmit = {this.handleSubmit}  method = "PUT"> */}
                      <div className="d-flex flex-row ">
                        <div className="pr-1">
                          <button
                            className="btn btn-outline-success"
                            onClick={() => {
                              axios
                                .put(
                                  `coordinatorProjectRequestManage/${req.id}/A`
                                )
                                .then(() => window.location.reload())
                                .catch((err) => console.log(err));
                              this.setState({ status: "A" });
                            }}
                          >
                            Accept
                          </button>
                        </div>
                        <div className="pl-1">
                          <button
                            className="btn btn-outline-danger "
                            onClick={() => {
                              axios
                                .put(
                                  `coordinatorProjectRequestManage/${req.id}/R`
                                )
                                .then(() => window.location.reload())
                                .catch((err) => console.log(err));
                              this.setState({ status: "R" });
                            }}
                          >
                            Reject
                          </button>
                        </div>
                      </div>
                      {/* </form> */}
                    </div>
                    <div className="col-md-6 col-12 d-flex link  align-items-center py-2">
                      <Link to={`/project/${req.project}`}>
                        <div className="text-primary">View Project Details</div>
                      </Link>
                    </div>
                  </div>
                </div>
              );
            } else {
              return null;
            }
          })}
      </div>
    );
  }
}

export default HandleRequests;

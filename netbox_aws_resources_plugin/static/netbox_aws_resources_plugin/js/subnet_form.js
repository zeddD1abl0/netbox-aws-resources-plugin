document.addEventListener('DOMContentLoaded', function () {
    // Helper function to get CSRF token (if not using jQuery's ajaxSetup)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    const vpcField = document.getElementById('id_aws_vpc');
    const vpcCIDRHiddenField = document.getElementById('id__vpc_cidr_for_filter');
    const vpcVRFHiddenField = document.getElementById('id__vpc_vrf_id_for_filter');
    const cidrBlockField = document.getElementById('id_cidr_block'); // The actual dependent dropdown

    if (vpcField && vpcCIDRHiddenField && vpcVRFHiddenField && cidrBlockField) {
        vpcField.addEventListener('change', function () {
            const vpcId = this.value;

            // Clear previous values and dependent field options
            vpcCIDRHiddenField.value = '';
            vpcVRFHiddenField.value = '';
            // Trigger change on hidden fields to clear/reset the cidr_block APISelect
            vpcCIDRHiddenField.dispatchEvent(new Event('change', { bubbles: true }));
            // vpcVRFHiddenField.dispatchEvent(new Event('change', { bubbles: true })); // Not strictly necessary if 'within' is primary trigger

            // If a VPC is selected, fetch its details
            if (vpcId) {
                fetch(`/api/plugins/netbox-aws-resources-plugin/aws-vpcs/${vpcId}/`, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json',
                        'X-CSRFToken': csrftoken // Include CSRF token if your API requires it for GET, though usually not
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok: ' + response.statusText);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data && data.cidr_block && data.cidr_block.prefix) {
                        vpcCIDRHiddenField.value = data.cidr_block.prefix;
                        // VRF ID can be null for global, ensure we handle that
                        vpcVRFHiddenField.value = data.cidr_block.vrf ? data.cidr_block.vrf.id : ''; 

                        // IMPORTANT: Trigger change event on the hidden fields so APISelect updates
                        vpcCIDRHiddenField.dispatchEvent(new Event('change', { bubbles: true }));
                        // vpcVRFHiddenField.dispatchEvent(new Event('change', { bubbles: true })); // Triggering on one might be enough
                    } else {
                        console.warn('Selected VPC does not have a cidr_block or prefix defined:', data);
                    }
                })
                .catch(error => {
                    console.error('Error fetching VPC details:', error);
                });
            }
        });

        // If there's an initial value for VPC (e.g., on edit page load or form error), trigger change.
        // Check if the vpcField (which is likely a Select2) has a value selected.
        // For APISelect, this might require a slight delay or listening to a select2-specific event if it's not a simple select.
        // A simple check after DOMContentLoaded might work for pre-filled values.
        if (vpcField.value) {
            // console.log("VPC field has initial value on load: ", vpcField.value);
            vpcField.dispatchEvent(new Event('change', { bubbles: true }));
        }

    } else {
        if (!vpcField) console.error('AWS VPC field (id_aws_vpc) not found.');
        if (!vpcCIDRHiddenField) console.error('Hidden VPC CIDR field (id__vpc_cidr_for_filter) not found.');
        if (!vpcVRFHiddenField) console.error('Hidden VPC VRF ID field (id__vpc_vrf_id_for_filter) not found.');
        if (!cidrBlockField) console.error('CIDR Block field (id_cidr_block) not found.');
    }
});

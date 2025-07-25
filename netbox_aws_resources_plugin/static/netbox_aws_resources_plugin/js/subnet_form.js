// Prevents the script from running multiple times if it's included more than once on a page.
if (!window.subnetFormLoaded) {
    window.subnetFormLoaded = true;

    document.addEventListener('DOMContentLoaded', function () {
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
        const cidrBlockSelect = document.getElementById('id_cidr_block');
        const azSelect = document.getElementById('id_availability_zone');

        if (vpcField && vpcCIDRHiddenField && vpcVRFHiddenField && cidrBlockSelect && azSelect) {
            // Disable dependent fields initially if no VPC is selected
            if (!vpcField.value) {
                cidrBlockSelect.disabled = true;
                azSelect.disabled = true;
            }

            function updateAZDropdown(zones) {
                // Clear current options
                azSelect.innerHTML = '';

                // Add blank option
                const blankOption = document.createElement('option');
                blankOption.value = '';
                blankOption.textContent = '---------';
                azSelect.appendChild(blankOption);

                // Populate with new zones
                if (zones && zones.length > 0) {
                    zones.forEach(zone => {
                        const option = document.createElement('option');
                        option.value = zone;
                        option.textContent = zone;
                        azSelect.appendChild(option);
                    });
                    azSelect.disabled = false;
                } else {
                    azSelect.disabled = true;
                }
            }

            vpcField.addEventListener('change', function () {
                const vpcId = this.value;

                // Always clear previous values and disable fields
                vpcCIDRHiddenField.value = '';
                vpcVRFHiddenField.value = '';
                cidrBlockSelect.disabled = true;
                updateAZDropdown([]); // Clear and disable AZ dropdown

                // Trigger change on hidden fields to clear the cidr_block APISelect
                vpcCIDRHiddenField.dispatchEvent(new Event('change', { bubbles: true }));

                if (vpcId) {
                    fetch(`/api/plugins/netbox-aws-resources-plugin/aws-vpcs/${vpcId}/`, {
                        method: 'GET',
                        headers: {
                            'Accept': 'application/json',
                            'X-CSRFToken': csrftoken
                        }
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok: ' + response.statusText);
                        }
                        return response.json();
                    })
                    .then(data => {
                        // Update CIDR Block field
                        if (data && data.cidr_block && data.cidr_block.prefix) {
                            cidrBlockSelect.disabled = false;
                            vpcCIDRHiddenField.value = data.cidr_block.prefix;
                            vpcVRFHiddenField.value = data.cidr_block.vrf ? data.cidr_block.vrf.id : '';
                            vpcCIDRHiddenField.dispatchEvent(new Event('change', { bubbles: true }));
                            vpcVRFHiddenField.dispatchEvent(new Event('change', { bubbles: true }));
                        } else {
                            console.warn('Selected VPC does not have a cidr_block or prefix defined:', data);
                        }

                        // Update Availability Zone dropdown
                        if (data && data.availability_zones) {
                            updateAZDropdown(data.availability_zones);
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching VPC details:', error);
                        // Ensure fields remain disabled on error
                        cidrBlockSelect.disabled = true;
                        updateAZDropdown([]);
                    });
                }
            });

            // On page load, if a VPC is already selected (e.g., on an edit page),
            // trigger the change event to populate the dependent fields.
            if (vpcField.value) {
                vpcField.dispatchEvent(new Event('change', { bubbles: true }));
            }

        } else {
            if (!vpcField) console.error('AWS VPC field (id_aws_vpc) not found.');
            if (!vpcCIDRHiddenField) console.error('Hidden VPC CIDR field (id__vpc_cidr_for_filter) not found.');
            if (!vpcVRFHiddenField) console.error('Hidden VPC VRF ID field (id__vpc_vrf_id_for_filter) not found.');
            if (!cidrBlockSelect) console.error('CIDR Block select widget (id_cidr_block) not found.');
            if (!azSelect) console.error('Availability Zone select widget (id_availability_zone) not found.');
        }
    });

} // End of window.subnetFormLoaded check
